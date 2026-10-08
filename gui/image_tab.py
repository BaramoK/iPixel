"""Onglet Image : glisser-déposer d'image, aperçu, envoi au panneau LED."""
import tkinter as tk
from tkinter import ttk, messagebox
from tkinterdnd2 import DND_FILES
from PIL import Image, ImageTk
import os

from pypixelcolor import ResizeMethod

import history_manager as hm


class ImageTab(ttk.Frame):
    PREVIEW_SIZE = (200, 200)
    SUPPORTED_EXT = (".png", ".jpg", ".jpeg", ".bmp", ".gif")

    def __init__(self, parent, controller, config, on_status, on_send_success=None):
        super().__init__(parent)
        self.controller = controller
        self.config = config
        self.on_status = on_status
        self.on_send_success = on_send_success
        # Id de l'entrée d'historique rechargée (None si contenu neuf)
        self.source_entry_id = None
        self.current_path = None
        self._photo = None

        self._build_ui()
        self._load_config()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Zone de drop + preview
        left = ttk.Frame(self)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.drop_frame = ttk.LabelFrame(left, text=" Glisser-déposer ", padding=10)
        self.drop_frame.pack(fill=tk.BOTH, expand=True)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="Glissez une image ici\n(.png .jpg .gif .bmp)",
            bg="#2b2b2b",
            fg="#ffffff",
            justify=tk.CENTER,
            font=("Segoe UI", 12, "bold"),
        )
        self.drop_label.pack(fill=tk.BOTH, expand=True)

        # DnD registration
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind("<<Drop>>", self._on_drop)

        # Preview
        self.preview_label = tk.Label(self.drop_frame, bg="#1e1e1e")
        self.preview_label.pack(pady=(8, 0))

        # Options à droite
        right = ttk.Frame(self, width=220)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        right.pack_propagate(False)

        # Resize method
        ttk.Label(right, text="Mode redimensionnement").pack(anchor=tk.W, pady=(10, 2))
        self.resize_var = tk.StringVar(value="FIT")
        self.resize_combo = ttk.Combobox(
            right,
            textvariable=self.resize_var,
            values=[e.name for e in ResizeMethod],
            state="readonly",
        )
        self.resize_combo.pack(fill=tk.X)

        # Save slot
        ttk.Label(right, text="Slot de sauvegarde (0 = aucun)").pack(anchor=tk.W, pady=(10, 2))
        self.slot_var = tk.IntVar(value=0)
        self.slot_spin = ttk.Spinbox(right, from_=0, to_=20, textvariable=self.slot_var, width=10)
        self.slot_spin.pack(anchor=tk.W)

        # Chemin
        self.path_label = ttk.Label(right, text="Aucune image", wraplength=200)
        self.path_label.pack(anchor=tk.W, pady=(15, 0))

        # Bouton envoyer
        self.send_btn = ttk.Button(right, text="📤 Envoyer au panneau", command=self._on_send)
        self.send_btn.pack(fill=tk.X, pady=(20, 5))

        # Bouton clear preview
        self.clear_btn = ttk.Button(right, text="🗑️ Réinitialiser", command=self._clear)
        self.clear_btn.pack(fill=tk.X)

    # ------------------------------------------------------------------
    # DnD Handler
    # ------------------------------------------------------------------
    def _on_drop(self, event):
        path = event.data.strip()
        # tkinterdnd2 peut encadrer avec des {} s'il y a des espaces
        if path.startswith("{") and path.endswith("}"):
            path = path[1:-1]
        if os.path.isfile(path):
            ext = os.path.splitext(path)[1].lower()
            if ext in self.SUPPORTED_EXT:
                self.source_entry_id = None
                self._load_image(path)
            else:
                messagebox.showwarning("Format non supporté", f"Extension '{ext}' non prise en charge.")
        else:
            messagebox.showwarning("Fichier invalide", "Le chemin déposé ne correspond pas à un fichier.")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _load_image(self, path):
        self.current_path = path
        self.path_label.config(text=os.path.basename(path))
        try:
            img = Image.open(path)
            img.thumbnail(self.PREVIEW_SIZE, Image.Resampling.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=self._photo)
            self.on_status(f"Image chargée : {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Erreur chargement image", str(e))
            self._clear()

    def _clear(self):
        self.current_path = None
        self.source_entry_id = None
        self.path_label.config(text="Aucune image")
        self.preview_label.config(image="")
        self._photo = None
        self.on_status("Prêt")

    def _on_send(self):
        if not self.current_path:
            messagebox.showinfo("Information", "Veuillez d'abord glisser une image.")
            return
        if not self.controller.is_connected():
            messagebox.showwarning("Non connecté", "Veuillez d'abord connecter le panneau LED.")
            return

        self.send_btn.config(state=tk.DISABLED)
        self.on_status("Envoi de l'image en cours…", busy=True)

        resize_name = self.resize_var.get()
        resize_method = ResizeMethod[resize_name]
        slot = self.slot_var.get() or None

        def task():
            try:
                self.controller.send_image(self.current_path, resize_method=resize_method, save_slot=slot)
                return None
            except Exception as e:
                return e

        def on_done(future):
            err = future.result()
            self.send_btn.config(state=tk.NORMAL)
            if err:
                self.on_status(f"Erreur envoi image : {err}", error=True)
                messagebox.showerror("Erreur envoi", str(err))
            else:
                self.on_status("Image envoyée avec succès !")
                self._save_config()
                if self.on_send_success:
                    self.on_send_success(
                        "image",
                        os.path.basename(self.current_path),
                        {
                            "path": self.current_path,
                            "resize_method": self.resize_var.get(),
                            "slot": self.slot_var.get(),
                        },
                        self.source_entry_id,
                    )

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------
    def _load_config(self):
        self.resize_var.set(self.config.get("image_resize", "FIT"))
        self.slot_var.set(self.config.get("image_slot", 0))

    def _save_config(self):
        self.config["image_resize"] = self.resize_var.get()
        self.config["image_slot"] = self.slot_var.get()

    def populate_from_data(self, data: dict, entry_id=None):
        """Charge une image depuis les données d'un historique.

        ``entry_id`` (optionnel) mémorise l'entrée d'origine afin de la mettre
        à jour au prochain envoi plutôt que de créer un doublon.
        """
        path = hm.resolve_image_path(data)
        if os.path.isfile(path):
            self._load_image(path)
        else:
            self._clear()
            self.on_status(f"Image introuvable : {path}", error=True)
        self.resize_var.set(data.get("resize_method", "FIT"))
        self.slot_var.set(data.get("slot", 0))
        self.source_entry_id = entry_id
