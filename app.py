"""Point d'entrée de l'application iPixel UI Manager."""
import os
import sys

from tkinterdnd2 import TkinterDnD

from gui.main_window import MainWindow


def _resolve_icon_path() -> str | None:
    """Retourne le chemin absolu de l'icône (mode dev ou frozen PyInstaller)."""
    if hasattr(sys, "_MEIPASS"):
        # Mode PyInstaller (fichier extrait dans le dossier temporaire)
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    icon = os.path.join(base, "assets", "app_icon.ico")
    return icon if os.path.isfile(icon) else None


def main():
    root = TkinterDnD.Tk()
    root.title("iPixel UI Manager")
    root.geometry("900x650")
    root.minsize(700, 500)

    icon_path = _resolve_icon_path()
    if icon_path:
        root.iconbitmap(icon_path)

    app = MainWindow(root)
    app.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
