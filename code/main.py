# global imports
import chess
import tkinter as tk
from PIL import Image, ImageTk

# local imports
from chess_gui import ChessGUI
from lichess_move_selection import Lichess_Move_Selector

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()