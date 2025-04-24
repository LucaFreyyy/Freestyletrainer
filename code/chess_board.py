# global imports
import tkinter as tk
import chess
import random
from PIL import Image, ImageTk

# local imports
from constants import *
from lichess_move_selection import Lichess_Move_Selector

# class specific constants
TILE_SIZE = 60
TOP_RANK_INDEX = 7
HIGHLIGHT_COLOR = "#FF0040"  # semi-transparent green overlay
LIGHT_SQUARE_COLOR = "#F0D9B5"
DARK_SQUARE_COLOR = "#B58863"

class ChessBoard(tk.Canvas):
    def __init__(self, parent, move_callback=None):
        super().__init__(parent, width=8*TILE_SIZE, height=8*TILE_SIZE)
        self.parent = parent
        self.on_move_made = move_callback
        self.selected_square = None
        self.highlight_squares = []
        self.flipped = False
        self.piece_images = {}
        
        # Initialize chess components
        self.board = chess.Board()
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
                    chess_file = file
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
            chess_file = file
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
                if self.flipped:
                    self.highlight_squares = [chess.square(7 - chess.square_file(sq), chess.square_rank(sq)) for sq in self.highlight_squares]
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
            if self.flipped:
                self.highlight_squares = [chess.square(7 - chess.square_file(sq), chess.square_rank(sq)) for sq in self.highlight_squares]
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
        else:
            # Invalid move - just deselect
            self.selected_square = None
            self.highlight_squares = []
            self.draw_board()

    def new_game(self):
        self.board.reset()
        self.selected_square = None
        self.highlight_squares = []
        self.draw_board()

    def flip_board(self):
        self.flipped = not self.flipped
        self.draw_board()