# global imports
import chess
import tkinter as tk
from PIL import Image, ImageTk

# local imports
from main_application import MainApplication
from chess_board import ChessBoard
from lichess_move_selection import Lichess_Move_Selector


def main():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    main()