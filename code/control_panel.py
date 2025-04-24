import tkinter as tk
import chess

class ControlPanel(tk.Frame):
    def __init__(self, parent, chess_board, move_list):
        super().__init__(parent)
        self.chess_board = chess_board
        self.move_list = move_list
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self, text="New Game", command=self.new_game).pack(pady=5)
        tk.Button(self, text="Flip Board", command=self.chess_board.flip_board).pack(pady=5)

    def new_game(self):
        self.chess_board.new_game()
        self.move_list.clear()