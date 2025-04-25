# global imports
import chess
import random
import tkinter as tk

# local imports
from constants import *
from chess_board import ChessBoard
from control_panel import ControlPanel
from move_list import MoveList
from eval_list import EvalList

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chess GUI")
        self.geometry("1100x700")
        
        # Configure main layout
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create components
        self.move_list = MoveList(self.main_frame)
        self.eval_list = EvalList(self.main_frame)
        self.chess_board = ChessBoard(self.main_frame, self.on_move_made)
        self.control_panel = ControlPanel(self.main_frame, self.chess_board, self.move_list, self.eval_list)
        
        # Layout components side by side without overlaps
        self.chess_board.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NSEW)
        self.move_list.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NS)
        self.eval_list.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NS)
        self.control_panel.grid(row=0, column=3, padx=10, pady=10, sticky=tk.NS)
        
        # Adjust grid weights for better layout
        self.main_frame.grid_columnconfigure(0, weight=3)  # Chess board gets more space
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(3, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)  # Main row gets all vertical space



    def on_move_made(self, san, is_white_move):
        """Callback for chess board moves"""
        self.move_list.add_move(san, is_white_move)