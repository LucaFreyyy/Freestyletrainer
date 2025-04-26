# global imports
import tkinter as tk
import chess

# local imports
from position_eval import Evaluator

class ControlPanel(tk.Frame):
    def __init__(self, parent, chess_board, move_list, eval_list):
        super().__init__(parent)
        self.chess_board = chess_board
        self.move_list = move_list
        self.start_position_number = tk.StringVar(value=self.get_start_position_number())
        self.eval_label = tk.Label(self, text="Evaluation: ", font=('Arial', 12))
        self.eval_label.pack(pady=5)
        self.eval_list = eval_list
        self.evaluator = Evaluator(self.eval_label, self.eval_list)
        self.chess_board.evaluator = self.evaluator
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Start Position Number:").pack(pady=5)
        tk.Label(self, textvariable=self.start_position_number).pack(pady=5)
        tk.Button(self, text="New Game", command=self.new_game).pack(pady=5)
        tk.Button(self, text="Flip Board", command=self.flip_board).pack(pady=5)
        
    def new_game(self):
        self.move_list.clear()
        self.eval_list.clear()
        self.chess_board.new_game()
        self.update_start_position_number()

    def flip_board(self):
        self.chess_board.flip_board()
        self.new_game()

    def get_start_position_number(self):
        # Convert the FEN to a unique number (example logic, adjust as needed)
        fen = self.chess_board.start_position_id
        return fen

    def update_start_position_number(self):
        self.start_position_number.set(self.get_start_position_number())