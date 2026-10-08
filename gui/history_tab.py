"""Onglet Historique : liste des envois, ré-émission, suppression."""
import os
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk
from pypixelcolor import TextAnimation, ResizeMethod
from pypixelcolor.lib.font_config import FontConfig

import history_manager as hm


class HistoryTab(ttk.Frame):
    THUMB_SIZE = (40, 40)

    def __init__(self, parent, notebook, controller, text_tab, image_tab, on_status):
        super().__init__(parent)
        self.notebook = notebook
        self.controller = controller
        self.text_tab = text_tab
        self.image_tab = image_tab
        self.on_status = on_status
        self._thumb_refs = {}

        self._build_ui()
        self.refresh_list()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Liste
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        columns = ("datetime", "type", "label", "slot", "mode", "status")
        style = ttk.Style(self)
        style.configure("History.Treeview", rowheight=self.THUMB_SIZE[1] + 8)
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show=("tree", "headings"),
            selectmode="browse", style="History.Treeview",
        )
        self.tree.heading("#0", text="Aperçu")
        self.tree.heading("datetime", text="Date / Heure")
        self.tree.heading("type", text="Type")
        self.tree.heading("label", text="Contenu")
        self.tree.heading("slot", text="Slot")
        self.tree.heading("mode", text="Mode")
        self.tree.heading("status", text="Statut")
        self.tree.column("#0", width=self.THUMB_SIZE[0] + 16,
                         minwidth=self.THUMB_SIZE[0] + 16, stretch=False, anchor="center")
        self.tree.column("datetime", width=130, anchor="w")
        self.tree.column("type", width=80, anchor="center")
        self.tree.column("label", width=260, anchor="w")
        self.tree.column("slot", width=50, anchor="center")
        self.tree.column("mode", width=70, anchor="center")
        self.tree.column("status", width=60, anchor="center")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self._on_double_click)

        # Boutons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.load_btn = ttk.Button(
            btn_frame, text="📂 Charger dans l'onglet",
            command=self._on_load_to_tab
        )
        self.load_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.send_btn = ttk.Button(
            btn_frame, text="🚀 Envoyer directement",
            command=self._on_send_direct
        )
        self.send_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.del_btn = ttk.Button(
            btn_frame, text="🗑️ Supprimer la sélection",
            command=self._on_delete
        )
        self.del_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.clear_btn = ttk.Button(
            btn_frame, text="💣 Vider tout l'historique",
            command=self._on_clear_all
        )
        self.clear_btn.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_selected_entry(self):
        selection = self.tree.selection()
        if not selection:
            return None
        entry_id = selection[0]
        for entry in hm.load_history():
            if entry.get("id") == entry_id:
                return entry
        return None

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._thumb_refs.clear()
        entries = hm.load_history()
        for entry in reversed(entries):
            label = entry.get("label", "")
            if len(label) > 50:
                label = label[:47] + "..."
            type_icon = "📝" if entry.get("type") == "text" else "🖼️"
            thumb = self._make_thumbnail(entry)
            self.tree.insert(
                "", tk.END, iid=entry.get("id"),
                image=thumb if thumb else "",
                values=(
                    entry.get("timestamp", ""),
                    type_icon,
                    label,
                    self._format_slot(entry),
                    self._format_mode(entry),
                    entry.get("status", ""),
                ),
            )

    def _format_slot(self, entry: dict) -> str:
        """Numéro de slot de sauvegarde (0 ou absent = aucun) → « — »."""
        slot = (entry.get("data") or {}).get("slot") or 0
        return str(slot) if slot else "—"

    def _format_mode(self, entry: dict) -> str:
        """Mode de redimensionnement (images uniquement) : FIT / CROP."""
        if entry.get("type") != "image":
            return "—"
        return (entry.get("data") or {}).get("resize_method") or "FIT"

    def _make_thumbnail(self, entry: dict):
        """Génère la miniature d'une entrée image (référence conservée dans _thumb_refs)."""
        if entry.get("type") != "image":
            return None
        path = hm.resolve_image_path(entry.get("data", {}))
        if not path or not os.path.isfile(path):
            return None
        try:
            img = Image.open(path)
            img.thumbnail(self.THUMB_SIZE, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._thumb_refs[entry.get("id")] = photo
            return photo
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _on_double_click(self, event=None):
        self._on_load_to_tab()

    def _on_load_to_tab(self):
        entry = self._get_selected_entry()
        if not entry:
            messagebox.showinfo("Information", "Veuillez sélectionner un élément.")
            return
        data = entry.get("data", {})
        if entry.get("type") == "text":
            self.text_tab.populate_from_data(data, entry.get("id"))
            self.notebook.select(self.text_tab)
            self.on_status("Chargé dans l'onglet Texte")
        elif entry.get("type") == "image":
            self.image_tab.populate_from_data(data, entry.get("id"))
            self.notebook.select(self.image_tab)
            self.on_status("Chargé dans l'onglet Image")

    def _on_send_direct(self):
        entry = self._get_selected_entry()
        if not entry:
            messagebox.showinfo("Information", "Veuillez sélectionner un élément.")
            return
        if not self.controller.is_connected():
            messagebox.showwarning("Non connecté", "Veuillez d'abord connecter le panneau LED.")
            return
        self.send_btn.config(state=tk.DISABLED)
        self.on_status("Ré-émission en cours…", busy=True)

        def task():
            try:
                data = entry.get("data", {})
                if entry.get("type") == "text":
                    self._send_text_direct(data)
                elif entry.get("type") == "image":
                    self._send_image_direct(data)
                return None
            except Exception as e:
                return e

        def on_done(future):
            err = future.result()
            self.send_btn.config(state=tk.NORMAL)
            if err:
                self.on_status(f"Erreur ré-émission : {err}", error=True)
                messagebox.showerror("Erreur ré-émission", str(err))
            else:
                self.on_status("Ré-émission réussie !")

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    def _send_text_direct(self, data: dict):
        animation = TextAnimation[data.get("animation", "STATIC")]
        speed = data.get("speed", 50)
        color = data.get("color", "ffffff")
        bg_color = data.get("bg_color")
        save_slot = data.get("slot") or None
        font_path = data.get("font_path", "")
        size = data.get("font_size", 16)
        if font_path and os.path.isfile(font_path):
            font = FontConfig.from_file(font_path, font_size=size)
        else:
            font = "UNIFONT"
        self.controller.send_text(
            data.get("text", ""), animation=animation, speed=speed,
            color=color, bg_color=bg_color, save_slot=save_slot, font=font,
        )

    def _send_image_direct(self, data: dict):
        path = hm.resolve_image_path(data)
        if not path or not os.path.isfile(path):
            raise FileNotFoundError(f"Image introuvable : {data.get('path', '')}")
        resize_method = ResizeMethod[data.get("resize_method", "FIT")]
        save_slot = data.get("slot") or None
        self.controller.send_image(path, resize_method=resize_method, save_slot=save_slot)

    def _on_delete(self):
        entry = self._get_selected_entry()
        if not entry:
            messagebox.showinfo("Information", "Veuillez sélectionner un élément.")
            return
        if messagebox.askyesno(
            "Confirmer",
            f"Supprimer cet élément de l'historique ?\n\n{entry.get('label', '')}",
        ):
            hm.remove_entry(entry.get("id"))
            self.refresh_list()
            self.on_status("Élément supprimé")

    def _on_clear_all(self):
        if messagebox.askyesno(
            "Confirmer",
            "Voulez-vous vraiment vider tout l'historique ?\nCette action est irréversible.",
        ):
            hm.clear_history()
            self.refresh_list()
            self.on_status("Historique vidé")

    def add_entry(self, entry_type: str, label: str, data: dict,
                  status: str = "success", source_entry_id=None):
        """Ajoute ou met à jour une entrée puis rafraîchit la liste.

        Si ``source_entry_id`` est fourni (envoi d'un élément rechargé depuis
        l'historique), l'entrée existante est mise à jour au lieu d'être
        dupliquée (timestamp et position conservés).
        """
        if source_entry_id:
            hm.update_entry(source_entry_id, entry_type, label, data, status=status)
        else:
            hm.add_entry(entry_type, label, data, status=status)
        self.refresh_list()

