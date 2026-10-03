"""Fenêtre principale iPixel UI Manager."""
import tkinter as tk
from tkinter import ttk, messagebox

from gui.image_tab import ImageTab
from gui.text_tab import TextTab
from gui.settings_tab import SettingsTab
from gui.history_tab import HistoryTab
from led_client import LEDController
from config_manager import load_config, save_config


class MainWindow(tk.Frame):
    """Assemble la barre de connexion, le notebook et la barre d'état."""

    def __init__(self, root: tk.Tk):
        super().__init__(root)
        self.root = root
        self.config = load_config()
        self.controller = LEDController(address=self.config.get("mac_address"))
        self._build_ui()
        self._update_status("Déconnecté")

    def _build_ui(self):
        # --- Barre supérieure ---
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(top, text="Adresse MAC :").pack(side=tk.LEFT)
        self.mac_var = tk.StringVar(value=self.config.get("mac_address", ""))
        self.mac_entry = ttk.Entry(top, textvariable=self.mac_var, width=20)
        self.mac_entry.pack(side=tk.LEFT, padx=5)

        self.connect_btn = ttk.Button(top, text="🔗 Connecter", command=self._on_connect)
        self.connect_btn.pack(side=tk.LEFT, padx=5)

        self.disconnect_btn = ttk.Button(top, text="⛓️‍💥 Déconnecter", command=self._on_disconnect)
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        self.disconnect_btn.config(state=tk.DISABLED)

        ttk.Button(top, text="🔍 Scanner", command=self._on_scan).pack(side=tk.LEFT, padx=5)

        self.devices_var = tk.StringVar()
        self.devices_combo = ttk.Combobox(
            top, textvariable=self.devices_var, state="readonly", width=30
        )
        self.devices_combo.pack(side=tk.LEFT, padx=5)
        self.devices_combo.bind("<<ComboboxSelected>>", self._on_device_selected)

        # --- Notebook ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.image_tab = ImageTab(
            self.notebook, self.controller, self.config, self._update_status
        )
        self.text_tab = TextTab(
            self.notebook, self.controller, self.config, self._update_status
        )
        self.settings_tab = SettingsTab(
            self.notebook, self.controller, self.config, self._update_status
        )
        self.history_tab = HistoryTab(
            self.notebook,
            self.notebook,
            self.controller,
            self.text_tab,
            self.image_tab,
            self._update_status,
        )

        # Connecter les callbacks d'historique après création
        self.text_tab.on_send_success = self._on_send_success
        self.image_tab.on_send_success = self._on_send_success

        self.notebook.add(self.image_tab, text="🖼️ Image")
        self.notebook.add(self.text_tab, text="📝 Texte")
        self.notebook.add(self.settings_tab, text="⚙️ Réglages")
        self.notebook.add(self.history_tab, text="🕘 Historique")

        # --- Barre d'état ---
        self.status_bar = ttk.Label(
            self, text="Prêt", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2)
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _update_status(self, msg: str, busy=False, error=False):
        self.status_bar.config(text=msg)
        if error:
            self.status_bar.config(foreground="red")
        elif busy:
            self.status_bar.config(foreground="blue")
        else:
            self.status_bar.config(foreground="black")

    def _on_send_success(self, entry_type: str, label: str, data: dict):
        """Appelé par les onglets Texte/Image pour enregistrer l'envoi dans l'historique."""
        self.history_tab.add_entry(entry_type, label, data, status="success")

    def _on_device_selected(self, event=None):
        val = self.devices_var.get()
        if "|" in val:
            mac = val.split("|")[0].strip()
            self.mac_var.set(mac)
            self.config["mac_address"] = mac

    def _on_scan(self):
        self._update_status("Scan BLE en cours…", busy=True)
        self.connect_btn.config(state=tk.DISABLED)

        def task():
            try:
                return self.controller.scan_devices(timeout=5.0)
            except Exception as e:
                return e

        def on_done(future):
            result = future.result()
            self.connect_btn.config(state=tk.NORMAL)
            if isinstance(result, Exception):
                self._update_status(f"Erreur scan: {result}", error=True)
                messagebox.showerror("Erreur scan", str(result))
            else:
                devices = result
                if not devices:
                    self._update_status("Aucun appareil trouvé.")
                    messagebox.showinfo("Scan", "Aucun appareil LED trouvé.")
                else:
                    items = [
                        f"{d.address} | {getattr(d, 'name', 'Unknown') or 'Unknown'}"
                        for d in devices
                    ]
                    self.devices_combo.config(values=items)
                    self.devices_var.set(items[0])
                    self._on_device_selected()
                    self._update_status(f"{len(devices)} appareil(s) trouvé(s).")

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    def _on_connect(self):
        mac = self.mac_var.get().strip()
        if not mac:
            messagebox.showwarning("MAC requise", "Veuillez entrer une adresse MAC.")
            return
        self.config["mac_address"] = mac
        self.controller.address = mac

        self.connect_btn.config(state=tk.DISABLED)
        self._update_status(f"Connexion à {mac}…", busy=True)

        def task():
            try:
                self.controller.connect()
                return None
            except Exception as e:
                return e

        def on_done(future):
            err = future.result()
            self.connect_btn.config(state=tk.NORMAL)
            if err:
                self._update_status(f"Échec connexion: {err}", error=True)
                messagebox.showerror("Connexion échouée", str(err))
            else:
                self.disconnect_btn.config(state=tk.NORMAL)
                self._update_status(f"Connecté à {mac}")

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    def _on_disconnect(self):
        self._update_status("Déconnexion…", busy=True)

        def task():
            try:
                self.controller.disconnect()
                return None
            except Exception as e:
                return e

        def on_done(future):
            err = future.result()
            self.disconnect_btn.config(state=tk.DISABLED)
            if err:
                self._update_status(f"Erreur déconnexion: {err}", error=True)
            else:
                self._update_status("Déconnecté")

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    def on_close(self):
        save_config(self.config)
        if self.controller.is_connected():
            try:
                self.controller.disconnect()
            except Exception:
                pass
        self.root.destroy()

