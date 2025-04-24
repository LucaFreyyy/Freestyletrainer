# global imports
import chess
import tkinter as tk
from PIL import Image, ImageTk

# local imports
from chess_gui import ChessGUI

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()