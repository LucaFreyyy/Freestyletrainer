import tkinter as tk

class MoveList(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.move_number = 1
        self.listbox = tk.Listbox(self, width=25, height=20, font=('Courier', 10))
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def add_move(self, san, is_white_move):
        if is_white_move:
            # New move pair with number
            entry = f"{self.move_number:>3}. {san}"
            self.listbox.insert(tk.END, entry)
        else:
            # Add black move to existing line
            last_index = self.listbox.size() - 1
            if last_index >= 0:
                current_text = self.listbox.get(last_index)
                new_text = f"{current_text} {san}"
                self.listbox.delete(last_index)
                self.listbox.insert(last_index, new_text)
                self.move_number += 1
        
        self.listbox.yview(tk.END)

    def clear(self):
        self.listbox.delete(0, tk.END)
        self.move_number = 1