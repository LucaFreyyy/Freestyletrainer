# global imports
import requests
from threading import Thread
from stockfish import Stockfish

# local imports
from constants import *

class Evaluator:
    def __init__(self, eval_label, eval_list):
        self.evaluation_cache = {}  # Store evaluations to avoid duplicate requests
        self.current_evaluation = None
        self.evaluation_thread = None
        self.eval_label = eval_label  # Reference to the label to update evaluation display
        self.eval_list = eval_list  # Reference to the eval list to update evaluations
        self.stockfish = Stockfish(path=STOCKFISH_PATH, parameters={"Threads": 2, "Minimum Thinking Time": 30})

    def get_cloud_evaluation(self, fen):
        """Fetch evaluation from Lichess cloud API"""
        if fen in self.evaluation_cache:
            return self.evaluation_cache[fen]
            
        try:
            url = f"https://lichess.org/api/cloud-eval?fen={fen}&multiPv=1"
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if 'error' not in data:
                    self.evaluation_cache[fen] = data
                    return data
        except Exception as e:
            print(f"Error fetching evaluation: {e}")

        return self.get_stockfish_evaluation(fen)  # Fallback to local evaluation
    
    def update_evaluation_display(self):
        current_eval = self.get_current_evaluation()
        self.eval_label.config(text=current_eval)
        is_white_move = 'b' in self.current_evaluation['fen'].split(' ')[1]
        self.eval_list.add_eval(current_eval, is_white_move)

    def fetch_evaluation_async(self, fen):
        """Fetch evaluation in background thread"""
        def worker():
            evaluation = self.get_cloud_evaluation(fen)
            if evaluation:
                self.current_evaluation = evaluation
                self.update_evaluation_display()
        
        if self.evaluation_thread and self.evaluation_thread.is_alive():
            self.evaluation_thread.join(timeout=0.1)
            
        self.evaluation_thread = Thread(target=worker)
        self.evaluation_thread.start()

    def get_stockfish_evaluation(self, fen):
        """Get evaluation from Stockfish and format it like cloud evaluation"""
        try:
            self.stockfish.set_fen_position(fen)
            evaluation = self.stockfish.get_evaluation()
            if evaluation["type"] == "mate":
                return {
                    "fen": fen,
                    "pvs": [{"mate": evaluation["value"]}]
                }
            elif evaluation["type"] == "cp":
                return {
                    "fen": fen,
                    "pvs": [{"cp": evaluation["value"]}]
                }
        except Exception as e:
            print(f"Error with Stockfish evaluation: {e}")
        return None
        
    def get_current_evaluation(self):
        if self.current_evaluation:
            eval_data = self.current_evaluation
            cp = eval_data.get('pvs', [{}])[0].get('cp')
            mate = eval_data.get('pvs', [{}])[0].get('mate')
            
            if mate:
                return f"Mate in {abs(mate)}" + (" ♔" if mate > 0 else " ♚")
            elif cp:
                score = cp / 100
                return f"{'+' if score > 0 else ''}{score:.1f}"
        return "No eval"