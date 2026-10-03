"""Onglet Réglages : luminosité, orientation, alimentation, horloge, slots."""
import tkinter as tk
from tkinter import ttk, messagebox


class SettingsTab(ttk.Frame):
    def __init__(self, parent, controller, config, on_status):
        super().__init__(parent)
        self.controller = controller
        self.config = config
        self.on_status = on_status

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        bright_frame = ttk.LabelFrame(left, text=" Luminosité ", padding=10)
        bright_frame.pack(fill=tk.X, pady=(0, 10))
        self.bright_var = tk.IntVar(value=50)
        self.bright_scale = ttk.Scale(
            bright_frame, from_=0, to_=100, orient=tk.HORIZONTAL, variable=self.bright_var,
            command=lambda v: self.bright_label.config(text=f"{int(float(v))}%")
        )
        self.bright_scale.pack(fill=tk.X)
        self.bright_label = ttk.Label(bright_frame, text="50%")
        self.bright_label.pack(anchor=tk.E)
        ttk.Button(bright_frame, text="Appliquer", command=self._apply_brightness).pack(anchor=tk.E, pady=(5, 0))

        orient_frame = ttk.LabelFrame(left, text=" Orientation ", padding=10)
        orient_frame.pack(fill=tk.X, pady=(0, 10))
        self.orient_var = tk.IntVar(value=0)
        orient_combo = ttk.Combobox(
            orient_frame,
            textvariable=self.orient_var,
            values=[0, 1, 2, 3],
            state="readonly",
            width=10,
        )
        orient_combo.grid(row=0, column=0)
        ttk.Label(orient_frame, text="0°  90°  180°  270°").grid(row=0, column=1, padx=8)
        ttk.Button(orient_frame, text="Appliquer", command=self._apply_orientation).grid(row=0, column=2, padx=(10, 0))

        power_frame = ttk.LabelFrame(left, text=" Alimentation ", padding=10)
        power_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(power_frame, text="⏻ Allumer", command=lambda: self._set_power(True)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(power_frame, text="⭘ Éteindre", command=lambda: self._set_power(False)).pack(side=tk.LEFT)

        right = ttk.Frame(self)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        clock_frame = ttk.LabelFrame(right, text=" Horloge ", padding=10)
        clock_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(clock_frame, text="Style").grid(row=0, column=0, sticky=tk.W)
        self.clock_style = tk.IntVar(value=1)
        ttk.Spinbox(clock_frame, from_=1, to_=3, textvariable=self.clock_style, width=8).grid(row=0, column=1, padx=4)

        self.clock_24h = tk.BooleanVar(value=True)
        ttk.Checkbutton(clock_frame, text="Format 24h", variable=self.clock_24h).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        self.clock_date = tk.BooleanVar(value=True)
        ttk.Checkbutton(clock_frame, text="Afficher date", variable=self.clock_date).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        ttk.Button(clock_frame, text="Activer horloge", command=self._activate_clock).grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=tk.EW)

        slot_frame = ttk.LabelFrame(right, text=" Gestion des slots ", padding=10)
        slot_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(slot_frame, text="Numéro slot").grid(row=0, column=0, sticky=tk.W)
        self.slot_num = tk.IntVar(value=1)
        ttk.Spinbox(slot_frame, from_=1, to_=20, textvariable=self.slot_num, width=8).grid(row=0, column=1, padx=4)

        ttk.Button(slot_frame, text="▶ Afficher slot", command=self._show_slot).grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(8, 4))
        ttk.Button(slot_frame, text="🗑️ Supprimer slot", command=self._delete_slot).grid(row=2, column=0, columnspan=2, sticky=tk.EW)

        danger_frame = ttk.LabelFrame(right, text=" Danger Zone ", padding=10)
        danger_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(danger_frame, text="⚠️ Tout effacer (clear)", command=self._clear_all).pack(fill=tk.X)

    def _ensure_connected(self) -> bool:
        if not self.controller.is_connected():
            messagebox.showwarning("Non connecté", "Veuillez d'abord connecter le panneau LED.")
            return False
        return True

    def _run_task(self, fn, busy_msg, success_msg=None):
        if not self._ensure_connected():
            return
        self.on_status(busy_msg, busy=True)

        def task():
            try:
                fn()
                return None
            except Exception as e:
                return e

        def on_done(future):
            err = future.result()
            if err:
                self.on_status(f"Erreur : {err}", error=True)
                messagebox.showerror("Erreur", str(err))
            else:
                self.on_status(success_msg or "Commande appliquée.")
                self._save_config()

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    def _apply_brightness(self):
        val = self.bright_var.get()
        self._run_task(
            lambda: self.controller.set_brightness(val),
            "Application luminosité…",
            f"Luminosité réglée à {val}%",
        )

    def _apply_orientation(self):
        val = self.orient_var.get()
        self._run_task(
            lambda: self.controller.set_orientation(val),
            "Application orientation…",
            f"Orientation réglée à {val * 90}°",
        )

    def _set_power(self, on: bool):
        self._run_task(
            lambda: self.controller.set_power(on),
            "Changement d'alimentation…",
            "Alimentation modifiée.",
        )

    def _activate_clock(self):
        kwargs = {
            "style": self.clock_style.get(),
            "format_24": self.clock_24h.get(),
            "show_date": self.clock_date.get(),
        }
        self._run_task(
            lambda: self.controller.set_clock_mode(**kwargs),
            "Activation horloge…",
            "Horloge activée.",
        )

    def _show_slot(self):
        slot = self.slot_num.get()
        self._run_task(
            lambda: self.controller.show_slot(slot),
            f"Affichage du slot {slot}…",
            f"Slot {slot} affiché.",
        )

    def _delete_slot(self):
        slot = self.slot_num.get()
        if not messagebox.askyesno("Confirmation", f"Supprimer le contenu du slot {slot} ?"):
            return
        self._run_task(
            lambda: self.controller.delete(slot),
            f"Suppression du slot {slot}…",
            f"Slot {slot} supprimé.",
        )

    def _clear_all(self):
        if not messagebox.askyesno("Confirmation", "Effacer TOUTES les données et réglages du panneau ?"):
            return
        self._run_task(
            lambda: self.controller.clear(),
            "Effacement total en cours…",
            "Panneau réinitialisé.",
        )

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------
    def _load_config(self):
        self.bright_var.set(self.config.get("brightness", 50))
        self.orient_var.set(self.config.get("orientation", 0))

    def _save_config(self):
        self.config["brightness"] = self.bright_var.get()
        self.config["orientation"] = self.orient_var.get()
