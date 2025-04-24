# global imports
import tkinter as tk
import chess
import random
from PIL import Image, ImageTk

# local imports
from constants import *

# class specific constants
TILE_SIZE = 60
TOP_RANK_INDEX = 7
HIGHLIGHT_COLOR = "#FF0040"  # semi-transparent green overlay
LIGHT_SQUARE_COLOR = "#F0D9B5"
DARK_SQUARE_COLOR = "#B58863"

class ChessGUI:
    def __init__(self, root, starting_position=None):
        self.root = root
        self.canvas = tk.Canvas(root, width=BOARD_SIZE*TILE_SIZE, height=BOARD_SIZE*TILE_SIZE)
        self.canvas.pack()
        self.selected_square = None
        self.highlight_squares = []

        # Generate Chess960 position
        if starting_position is None:
            starting_position = random.randint(0, NUMBER_OF_START_POSITIONS - 1)
        self.board = chess.Board.from_chess960_pos(starting_position)
        self.piece_images = {}
        self.load_piece_images()
        self.draw_board()

        self.canvas.bind("<Button-1>", self.on_click)

    def load_piece_images(self):
        for color in PIECE_COLORS:
            for piece in PIECES:
                filename = f"{PIECE_PATH}{color}_{piece}.png"
                image = Image.open(filename).convert("RGBA")
                image = image.resize((TILE_SIZE, TILE_SIZE), Image.Resampling.LANCZOS)
                self.piece_images[f"{color}{piece}"] = ImageTk.PhotoImage(image)


    def draw_board(self):
        self.canvas.delete("all")
        colors = [LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR]

        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                x1 = file * TILE_SIZE
                y1 = rank * TILE_SIZE
                x2 = x1 + TILE_SIZE
                y2 = y1 + TILE_SIZE
                color = colors[(rank + file) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.board.piece_at(chess.square(file, TOP_RANK_INDEX - rank))
                if piece:
                    color = 'w' if piece.color == chess.WHITE else 'b'
                    symbol = piece.symbol().upper()
                    image_key = f"{color}{symbol}"
                    self.canvas.create_image(x1, y1, anchor=tk.NW, image=self.piece_images[image_key])
                    
        for square in self.highlight_squares:
            file = chess.square_file(square)
            rank = TOP_RANK_INDEX - chess.square_rank(square)
            x1 = file * TILE_SIZE
            y1 = rank * TILE_SIZE
            x2 = x1 + TILE_SIZE
            y2 = y1 + TILE_SIZE
            self.canvas.create_oval(x1 + 15, y1 + 15, x2 - 15, y2 - 15, fill=HIGHLIGHT_COLOR, outline="")


    def on_click(self, event):
        file = event.x // TILE_SIZE
        rank = TOP_RANK_INDEX - (event.y // TILE_SIZE)
        square = chess.square(file, rank)

        if self.selected_square is None:
            # Check if the clicked square has a piece of the current player's color
            piece = self.board.piece_at(square)
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = square
                self.highlight_squares = [move.to_square for move in self.board.legal_moves if move.from_square == square]
        else:
            # Attempt to make a move
            move = chess.Move(self.selected_square, square)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.selected_square = None
                self.highlight_squares = []
            else:
                # Check if the clicked square is another piece of the current player's color
                clicked_piece = self.board.piece_at(square)
                if clicked_piece is not None and clicked_piece.color == self.board.turn:
                    # Select the new piece
                    self.selected_square = square
                    self.highlight_squares = [move.to_square for move in self.board.legal_moves if move.from_square == square]
                else:
                    # Deselect
                    self.selected_square = None
                    self.highlight_squares = []
        self.draw_board()

