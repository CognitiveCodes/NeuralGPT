import tkinter as tk
from tkinter import filedialog

class DocumentEditor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, 'r') as f:
                return f.read()

    def save_file(self, data):
        file_path = filedialog.asksaveasfilename()
        if file_path:
            with open(file_path, 'w') as f:
                f.write(data)