# global imports
import tkinter as tk
import chess
import random
from PIL import Image, ImageTk
import requests

# local imports
from constants import *
from lichess_move_selection import Lichess_Move_Selector
from position_eval import Evaluator

# class specific constants
TILE_SIZE = 60
TOP_RANK_INDEX = 7
HIGHLIGHT_COLOR = "#FF0040"  # semi-transparent green overlay
LIGHT_SQUARE_COLOR = "#F0D9B5"
DARK_SQUARE_COLOR = "#B58863"

class ChessBoard(tk.Canvas):
    def __init__(self, parent, move_callback=None, evaluator=None):
        super().__init__(parent, width=8*TILE_SIZE, height=8*TILE_SIZE)
        self.parent = parent
        self.on_move_made = move_callback
        self.selected_square = None
        self.highlight_squares = []
        self.flipped = False
        self.piece_images = {}
        self.lichess_selector = Lichess_Move_Selector()
        self.evaluator = evaluator
        
        # Initialize chess components
        self.board = chess.Board(chess960=True)
        self.start_position_id = random.randint(0, 959)
        self.board.set_chess960_pos(self.start_position_id)
        self.start_position_fen = self.board.fen()
        self.load_piece_images()
        self.draw_board()
        self.bind("<Button-1>", self.on_click)

    def load_piece_images(self):
        for color in PIECE_COLORS:
            for piece in PIECES:
                filename = f"{PIECE_PATH}{color}_{piece}.png"
                image = Image.open(filename).convert("RGBA")
                image = image.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
                self.piece_images[f"{color}{piece}"] = ImageTk.PhotoImage(image)

    def draw_board(self):
        self.delete("all")
        for rank in range(8):
            for file in range(8):
                x1 = file * TILE_SIZE
                y1 = rank * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                color = LIGHT_SQUARE_COLOR if (rank + file) % 2 == 0 else DARK_SQUARE_COLOR
                self.create_rectangle(x1, y1, x2, y2, fill=color)
                
                # Calculate chess coordinates based on flip state
                if self.flipped:
                    chess_rank = rank
                    chess_file = TOP_RANK_INDEX - file
                else:
                    chess_rank = TOP_RANK_INDEX - rank
                    chess_file = file
                    
                square = chess.square(chess_file, chess_rank)
                piece = self.board.piece_at(square)
                if piece:
                    color = 'w' if piece.color == chess.WHITE else 'b'
                    symbol = piece.symbol().upper()
                    image_key = f"{color}{symbol}"
                    self.create_image(x1, y1, anchor=tk.NW, image=self.piece_images[image_key])

        # Draw highlights
        for square in self.highlight_squares:
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            if self.flipped:
                x = (7 - file) * TILE_SIZE
                y = rank * TILE_SIZE
            else:
                x = file * TILE_SIZE
                y = (7 - rank) * TILE_SIZE
            self.create_oval(x + 15, y + 15, x + TILE_SIZE - 15, y + TILE_SIZE - 15,
                           fill=HIGHLIGHT_COLOR, outline="")

    def on_click(self, event):
        # Convert click to chess coordinates
        file = event.x // TILE_SIZE
        rank = event.y // TILE_SIZE
        
        if self.flipped:
            chess_file = 7 - file
            chess_rank = rank
        else:
            chess_file = file
            chess_rank = 7 - rank
            
        square = chess.square(chess_file, chess_rank)
        piece = self.board.piece_at(square)

        # If no square is selected, select the clicked square if it's a piece of the current player's color
        if self.selected_square is None:
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.highlight_squares = [move.to_square for move in self.board.legal_moves 
                                        if move.from_square == square]
                self.draw_board()
            return

        # If we clicked on the same square, deselect it
        if square == self.selected_square:
            self.selected_square = None
            self.highlight_squares = []
            self.draw_board()
            return

        # Check if the clicked square contains our own piece (for piece switching)
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self.highlight_squares = [move.to_square for move in self.board.legal_moves 
                                    if move.from_square == square]
            self.draw_board()
            return

        # Try to make a move
        move = chess.Move(self.selected_square, square)
        
        # Check for pawn promotion
        if chess.square_rank(square) in [0, 7] and \
           self.board.piece_at(self.selected_square).piece_type == chess.PAWN:
            move.promotion = chess.QUEEN  # Default to queen promotion
        
        if move in self.board.legal_moves:
            # Get current turn before making the move
            is_white_move = self.board.turn == chess.WHITE

            # Generate SAN before pushing the move
            try:
                san = self.board.san(move)
            except AssertionError:
                san = move.uci()  # Fallback to UCI notation
            
            # Push move and update board
            self.board.push(move)
            self.selected_square = None
            self.highlight_squares = []
            
            # Pass color information to move list
            if self.on_move_made:
                self.on_move_made(san, is_white_move)
            
            self.draw_board()

            self.evaluate_position()

            # Let Lichess_Move_Selector play the next move if applicable
            if (self.board.turn == chess.BLACK and not self.flipped) or (self.board.turn == chess.WHITE and self.flipped):
                self.play_lichess_move()
        else:
            # Invalid move - just deselect
            self.selected_square = None
            self.highlight_squares = []
            self.draw_board()

    def play_lichess_move(self):
        move = self.lichess_selector.select_move(self.board)
        if move in self.board.legal_moves:
            # Generate SAN before pushing the move
            try:
                san = self.board.san(move)
            except AssertionError:
                san = move.uci()  # Fallback to UCI notation
            
            # Push move and update board
            self.board.push(move)
            self.selected_square = None
            self.highlight_squares = []
            
            # Pass color information to move list
            if self.on_move_made:
                self.on_move_made(san, self.board.turn == chess.BLACK)
            
            self.draw_board()

        self.evaluate_position()

    def new_game(self):
        self.board.reset()
        self.start_position_id = random.randint(0, 959)
        self.board.set_chess960_pos(self.start_position_id)
        self.start_position_fen = self.board.fen()
        self.selected_square = None
        self.highlight_squares = []
        self.draw_board()
        if self.flipped:
            self.play_lichess_move()

    def flip_board(self):
        self.flipped = not self.flipped
        self.draw_board()

    def evaluate_position(self):
        self.evaluator.fetch_evaluation_async(self.board.fen())