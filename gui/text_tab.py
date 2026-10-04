"""Onglet Texte : saisie de texte, couleurs, animation, envoi."""
import os
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog

import pypixelcolor
from pypixelcolor import TextAnimation
from pypixelcolor.lib.font_config import FontConfig


class TextTab(ttk.Frame):
    def __init__(self, parent, controller, config, on_status, on_send_success=None):
        super().__init__(parent)
        self.controller = controller
        self.config = config
        self.on_status = on_status
        self.on_send_success = on_send_success

        self._build_ui()
        self._load_config()

    def _build_ui(self):
        # Section texte
        frame_text = ttk.LabelFrame(self, text=" Texte ", padding=10)
        frame_text.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Zone de texte (tk.Text pour supporter l'Unicode hors-BMP)
        self.text_entry = tk.Text(frame_text, height=1, font=("Segoe UI", 12),
                                   bg="white", fg="black", relief=tk.SOLID, bd=1,
                                   wrap=tk.NONE, undo=True, padx=4, pady=2)
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.text_entry.bind("<Return>", lambda e: "break")        # bloque le retour à la ligne
        self.text_entry.bind("<Control-v>", self._on_paste)        # collage Unicode robuste
        self.text_entry.bind("<Control-V>", self._on_paste)

        # Bouton sélecteur d'emojis
        ttk.Button(frame_text, text="😀", width=3,
                   command=self._open_emoji_picker).pack(side=tk.LEFT, padx=(4, 0))

        # Options
        opts = ttk.Frame(self)
        opts.pack(fill=tk.X, padx=10, pady=5)

        # Couleurs
        col_frame = ttk.LabelFrame(opts, text=" Couleurs ", padding=8)
        col_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(col_frame, text="Texte (hex)").grid(row=0, column=0, sticky=tk.W)
        self.color_var = tk.StringVar(value="00ff00")
        self.color_entry = ttk.Entry(col_frame, textvariable=self.color_var, width=10)
        self.color_entry.grid(row=0, column=1, padx=4)
        ttk.Button(col_frame, text="🎨", width=3, command=lambda: self._pick_color(self.color_var)).grid(row=0, column=2)

        ttk.Label(col_frame, text="Fond (hex)").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.bg_var = tk.StringVar(value="")
        self.bg_entry = ttk.Entry(col_frame, textvariable=self.bg_var, width=10)
        self.bg_entry.grid(row=1, column=1, padx=4, pady=(8, 0))
        ttk.Button(col_frame, text="🎨", width=3, command=lambda: self._pick_color(self.bg_var)).grid(row=1, column=2, pady=(8, 0))

        # Animation + vitesse
        anim_frame = ttk.LabelFrame(opts, text=" Animation ", padding=8)
        anim_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(anim_frame, text="Type").grid(row=0, column=0, sticky=tk.W)
        self.anim_var = tk.StringVar(value="SCROLL_LEFT")
        self.anim_combo = ttk.Combobox(
            anim_frame,
            textvariable=self.anim_var,
            values=[e.name for e in TextAnimation],
            state="readonly",
            width=18,
        )
        self.anim_combo.grid(row=0, column=1, padx=4)

        ttk.Label(anim_frame, text="Vitesse").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.speed_var = tk.IntVar(value=50)
        self.speed_spin = ttk.Spinbox(anim_frame, from_=0, to_=100, textvariable=self.speed_var, width=10)
        self.speed_spin.grid(row=1, column=1, padx=4, pady=(8, 0))

        # Police et taille
        font_frame = ttk.LabelFrame(opts, text=" Police et taille ", padding=8)
        font_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Label(font_frame, text="Fichier").grid(row=0, column=0, sticky=tk.W)
        self.font_path_var = tk.StringVar()
        self.font_path_entry = ttk.Entry(font_frame, textvariable=self.font_path_var, width=18)
        self.font_path_entry.grid(row=0, column=1, padx=4)
        ttk.Button(font_frame, text="📁", width=3, command=self._browse_font).grid(row=0, column=2)

        ttk.Label(font_frame, text="Taille").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.font_size_var = tk.IntVar(value=16)
        self.font_size_spin = ttk.Spinbox(font_frame, from_=6, to=72, textvariable=self.font_size_var, width=10)
        self.font_size_spin.grid(row=1, column=1, padx=4, pady=(8, 0))

        # Slot + envoi
        slot_frame = ttk.LabelFrame(opts, text=" Options ", padding=8)
        slot_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(slot_frame, text="Slot").grid(row=0, column=0, sticky=tk.W)
        self.slot_var = tk.IntVar(value=0)
        ttk.Spinbox(slot_frame, from_=0, to_=20, textvariable=self.slot_var, width=10).grid(row=0, column=1, padx=4)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.send_btn = ttk.Button(btn_frame, text="📤 Envoyer au panneau", command=self._on_send)
        self.send_btn.pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(btn_frame, text="🗑️ Effacer", command=self._clear).pack(side=tk.LEFT)

        info = ttk.Label(
            self,
            text="Astuce : utilisez [#RRGGBB]…[/] pour des couleurs inline.",
            foreground="gray",
        )
        info.pack(anchor=tk.W, padx=10, pady=(0, 10))

    def _pick_color(self, var: tk.StringVar):
        raw = var.get()
        try:
            init_color = f"#{raw}"
        except Exception:
            init_color = "#000000"
        rgb, hx = colorchooser.askcolor(color=init_color, title="Choisir une couleur")
        if hx:
            var.set(hx.lstrip("#").lower())

    def _browse_font(self):
        path = filedialog.askopenfilename(
            title="Choisir une police",
            filetypes=[("Fichiers de police", "*.ttf *.otf"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.font_path_var.set(path)

    def _default_font(self):
        return "UNIFONT"

    # ------------------------------------------------------------------
    # Helpers texte
    # ------------------------------------------------------------------
    def _get_text(self):
        """Récupère le contenu du widget Text (sans le \\n final)."""
        return self.text_entry.get("1.0", "end-1c")

    def _set_text(self, value):
        """Remplace le contenu du widget Text."""
        self.text_entry.delete("1.0", tk.END)
        self.text_entry.insert("1.0", value)

    # ------------------------------------------------------------------
    # Collage Unicode + Emoji picker
    # ------------------------------------------------------------------
    def _on_paste(self, event=None):
        """Colle le contenu du presse-papiers proprement (Unicode)."""
        try:
            text = self.clipboard_get()
            self.text_entry.insert(tk.INSERT, text)
            return "break"
        except tk.TclError:
            return "break"

    _EMOJIS = {
        "Smileys": "😀😃😄😁😆😅😂🤣😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🥸🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👹👺🤡💩👻💀☠️👽👾🤖🎃😺😸😹😻😼😽🙀😿😾",
        "Cœurs & symboles": "❤️🧡💛💚💙💜🖤🤍🤎💔❣️💕💞💓💗💖💘💝💟☮️✝️☪️🕉️☸️✡️🔯🕎☯️☦️🛐⛎♈♉♊♋♌♍♎♏♐♑♒♓🆔⚛️🉑☢️☣️📴📳🈶🈚🈸🈺🈷️✴️🆚💮🉐㊙️㊗️🈴🈵🈹🈲🅰️🅱️🆎🆑🅾️🆘❌⭕🛑⛔📛🚫💯💢♨️🚷🚯🚳🚱🔞📵🚭❗❕❓❔‼️⁉️🔅🔆〽️⚠️🚸🔱⚜️🔰♻️✅🈯💹❇️✳️❎🌐💠Ⓜ️🌀💤🏧🚾♿🅿️🈳🈂🛂🛃🛄🛅",
        "Gestes & corps": "👍👎👊✊🤛🤜🤞✌️🤟🤘👌🤏👈👉👆👇☝️✋🤚🖐️🖖👋🤙💪🦾🖕✍️🙏🦶🦵🦿🦾💪👂🦻👃🧠🫀🫁🦷🦴👀👁️👅👄👶🧒👦👧🧑👱👨🧔👩🧓👴👵",
        "Animaux": "🐶🐱🐭🐹🐰🦊🐻🐼🐨🐯🦁🐮🐷🐽🐸🐵🙈🙉🙊🐒🐔🐧🐦🐤🐣🐥🦆🦅🦉🦇🐺🐗🐴🦄🐝🐛🦋🐌🐞🐜🦟🦗🕷️🕸️🦂🐢🐍🦎🦖🦕🐙🦑🦐🦞🦀🐡🐠🐟🐬🐳🐋🦈🐊🐅🐆🦓🦍🦧🐘🦛🦏🐪🐫🦒🦘🐃🐂🐄🐎🐖🐏🐑🦙🐐🦌🐕🦮🐕‍🦺🐈🐈‍⬛🐓🦃🦚🦜🦢🦩🕊️🐇🦝🦨🦡🦦🦥🐁🐀🐿️🦔",
        "Nourriture & boissons": "🍏🍎🍐🍊🍋🍌🍉🍇🍓🍈🍒🍑🍍🥝🥑🍅🍆🥒🥕🌽🌶️🥔🍠🥐🥖🍞🥨🥯🥞🧀🍖🍗🥩🥓🍔🍟🍕🌭🥪🌮🌯🥙🧆🥚🍳🥘🍲🥣🥗🍿🧈🧂🥫🍱🍘🍙🍚🍛🍜🍝🍠🍢🍣🍤🍥🍡🥟🥠🥡🦀🦞🦐🦑🍦🍧🍨🍩🍪🎂🍰🧁🥧🍫🍬🍭🍮🍯🍼🥛☕🫖🍵🍶🍾🍷🍸🍹🍺🍻🥂🥃🥤🧃🧉🧊",
        "Objets & jeux": "⌚📱💻⌨️🖥️🖨️🖱️🖲️🕹️🗜️💽💾💿📀📼📷📸📹🎥📽️🎞️📞☎️📟📠📺📻🎙️🎚️🎛️🧭⏱️⏲️⏰🕰️⌛⏳📡🔋🔌💡🔦🕯️🗑️🛢️💸💵💴💶💷💰💳💎⚖️🛠️⛓️🔫💣🧱🔪🗡️⚔️🛡️🚬⚰️⚱️🏺🔮📿💊💉🩸🩹🩼🩺🌡️🧹🧺🧻🚽🚰🚿🛁🛀🧼🪥🪒🧽🪣🧴🛎️🔑🗝️🚪🪑🛋️🛏️🛌🧸🖼️🪞🪟🛍️🛒🎁🎈🎏🎀🪄🪅🎊🎉🎎🏆🎖️🎗️🎟️🎫🔮🪄🎮🕹️🎰🎲🧩🧸🪀🪁",
    }

    def _open_emoji_picker(self):
        """Ouvre une popup avec une grille d'emojis cliquables."""
        win = tk.Toplevel(self)
        win.title("Sélecteur d'emojis")
        win.transient(self.winfo_toplevel())
        win.grab_set()
        win.resizable(False, False)

        # Centrer la fenêtre
        win.update_idletasks()
        w, h = 520, 400
        root = self.winfo_toplevel()
        x = root.winfo_x() + (root.winfo_width() // 2) - (w // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (h // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(win)
        scrollbar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0
        for category, emojis in self._EMOJIS.items():
            ttk.Label(scroll_frame, text=category,
                      font=("Segoe UI", 10, "bold")).grid(
                          row=row, column=0, sticky=tk.W,
                          padx=5, pady=(12, 4), columnspan=8)
            row += 1
            col = 0
            for emoji in emojis:
                btn = tk.Button(scroll_frame, text=emoji,
                                font=("Segoe UI Emoji", 14), width=2,
                                relief=tk.FLAT, cursor="hand2",
                                command=lambda e=emoji: self._insert_emoji(e))
                btn.grid(row=row, column=col, padx=1, pady=1)
                col += 1
                if col >= 8:
                    col = 0
                    row += 1
            row += 1

        ttk.Button(win, text="Fermer", command=win.destroy).pack(pady=8)

    def _insert_emoji(self, emoji):
        """Insère un emoji dans le champ texte."""
        self.text_entry.insert(tk.INSERT, emoji)
        self.text_entry.focus_set()

    def _clear(self):
        self._set_text("")
        self.on_status("Texte effacé")

    def _on_send(self):
        text = self._get_text().strip()
        if not text:
            messagebox.showinfo("Information", "Veuillez saisir un texte.")
            return
        if not self.controller.is_connected():
            messagebox.showwarning("Non connecté", "Veuillez d'abord connecter le panneau LED.")
            return

        self.send_btn.config(state=tk.DISABLED)
        self.on_status("Envoi du texte en cours…", busy=True)

        animation = TextAnimation[self.anim_var.get()]
        speed = self.speed_var.get()
        color = self.color_var.get().strip().lstrip("#")
        bg = self.bg_var.get().strip().lstrip("#")
        bg = bg if bg else None       # évite de passer "" à pypixelcolor → ValueError
        slot = self.slot_var.get() or None
        slot = slot if slot else None
        font_path = self.font_path_var.get().strip() or None
        size = self.font_size_var.get()

        if font_path == self._default_font() or not font_path:
            font = self._default_font()
        else:
            font = FontConfig.from_file(font_path, font_size=size)

        def task():
            try:
                self.controller.send_text(
                    text,
                    animation=animation,
                    speed=speed,
                    color=color,
                    bg_color=bg,
                    save_slot=slot,
                    font=font,
                )
                return None
            except Exception as e:
                return e

        def on_done(future):
            err = future.result()
            self.send_btn.config(state=tk.NORMAL)
            if err:
                self.on_status(f"Erreur envoi texte : {err}", error=True)
                messagebox.showerror("Erreur envoi", str(err))
            else:
                self.on_status("Texte envoyé avec succès !")
                self._save_config()
                if self.on_send_success:
                    self.on_send_success(
                        "text",
                        text[:50],
                        {
                            "text": text,
                            "animation": self.anim_var.get(),
                            "speed": self.speed_var.get(),
                            "color": self.color_var.get(),
                            "bg_color": self.bg_var.get(),
                            "slot": self.slot_var.get(),
                            "font_path": self.font_path_var.get(),
                            "font_size": self.font_size_var.get(),
                        },
                    )

        fut = self.controller.submit(task)
        fut.add_done_callback(lambda f: self.after(0, lambda: on_done(f)))

    # ------------------------------------------------------------------
    # Config persistence
    # ------------------------------------------------------------------
    def _load_config(self):
        self._set_text(self.config.get("last_text", ""))
        self.color_var.set(self.config.get("text_color", "00ff00"))
        self.bg_var.set(self.config.get("text_bg_color", "000000"))
        self.anim_var.set(self.config.get("text_animation", "SCROLL_LEFT"))
        self.speed_var.set(self.config.get("text_speed", 50))
        self.slot_var.set(self.config.get("text_slot", 0))
        self.font_path_var.set(self.config.get("text_font_path") or self._default_font())
        self.font_size_var.set(self.config.get("text_font_size", 16))

    def _save_config(self):
        self.config["last_text"] = self._get_text()
        self.config["text_color"] = self.color_var.get()
        self.config["text_bg_color"] = self.bg_var.get()
        self.config["text_animation"] = self.anim_var.get()
        self.config["text_speed"] = self.speed_var.get()
        self.config["text_slot"] = self.slot_var.get()
        self.config["text_font_path"] = self.font_path_var.get()
        self.config["text_font_size"] = self.font_size_var.get()

    def populate_from_data(self, data: dict):
        """Pré-remplit l'onglet avec les données d'un historique."""
        self._set_text(data.get("text", ""))
        self.color_var.set(data.get("color", "00ff00"))
        self.bg_var.set(data.get("bg_color", "000000"))
        self.anim_var.set(data.get("animation", "SCROLL_LEFT"))
        self.speed_var.set(data.get("speed", 50))
        self.slot_var.set(data.get("slot", 0))
        font_path = data.get("font_path", self._default_font())
        self.font_path_var.set(font_path if font_path else self._default_font())
        self.font_size_var.set(data.get("font_size", 16))
