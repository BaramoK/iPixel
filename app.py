"""Point d'entrée de l'application iPixel LED Controller."""
from tkinterdnd2 import TkinterDnD

from gui.main_window import MainWindow


def main():
    root = TkinterDnD.Tk()
    root.title("iPixel LED Controller")
    root.geometry("900x650")
    root.minsize(700, 500)

    app = MainWindow(root)
    app.pack(fill="both", expand=True)

    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
