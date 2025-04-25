import random
import requests
import chess

class Lichess_Move_Selector:
    def __init__(self):
        pass

    def select_move(self, board):
        # Get the FEN representation of the current board state
        fen = board.fen()

        # Fetch move statistics from the Lichess database
        data = self._fetch_lichess_data(fen)

        # Extract move statistics
        move_statistics = {move['uci']: move['white'] + move['black'] + move['draws'] for move in data.get('moves', [])}

        if not move_statistics:
            return None

        # Calculate the total number of moves played in this position
        total_moves = sum(move_statistics.values())

        # Create a list of moves and their probabilities
        moves, probabilities = zip(*[
            (move, count / total_moves) for move, count in move_statistics.items()
        ])

        # Select a move at random based on the probabilities
        selected_move = random.choices(moves, probabilities)[0]

        # Convert the UCI move to a chess.Move object
        selected_move = chess.Move.from_uci(selected_move)

        return selected_move
    
    """
    Fetch move statistics for the given board state from the Lichess API
    """
    def _fetch_lichess_data(self, fen, masters=False):
        if masters:
            url = f"https://explorer.lichess.ovh/masters?fen={fen}"
        else:
            url = f"https://explorer.lichess.ovh/lichess?fen={fen}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data from Lichess API: {response.status_code}")