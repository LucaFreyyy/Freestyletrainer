import requests
from threading import Thread

class Evaluator:
    def __init__(self, eval_label):
        self.evaluation_cache = {}  # Store evaluations to avoid duplicate requests
        self.current_evaluation = None
        self.evaluation_thread = None
        self.eval_label = eval_label  # Reference to the label to update evaluation display

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
        return None
    
    def update_evaluation_display(self):
        """Update the evaluation display in the GUI"""
        if self.current_evaluation:
            eval_data = self.current_evaluation
            cp = eval_data.get('pvs', [{}])[0].get('cp')
            mate = eval_data.get('pvs', [{}])[0].get('mate')
            
            if mate:
                eval_text = f"Mate in {abs(mate)}" + (" ♔" if mate > 0 else " ♚")
            elif cp:
                score = cp/100  # Convert centipawns to pawns
                eval_text = f"{'+' if score > 0 else ''}{score:.1f}"
            else:
                eval_text = "No evaluation"

            self.eval_label.config(text=eval_text)

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