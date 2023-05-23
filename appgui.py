import tkinter as tk
from utils import load_data, preprocess_data
from model import build_model, train_model, evaluate_model

# Define the GUI
class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.load_data_button = tk.Button(self)
        self.load_data_button["text"] = "Load Data"
        self.load_data_button["command"] = self.load_data
        self.load_data_button.pack(side="top")

        self.train_model_button = tk.Button(self)
        self.train_model_button["text"] = "Train Model"
        self.train_model_button["command"] = self.train_model
        self.train_model_button.pack(side="top")

        self.evaluate_model_button = tk.Button(self)
        self.evaluate_model_button["text"] = "Evaluate Model"
        self.evaluate_model_button["command"] = self.evaluate_model
        self.evaluate_model_button.pack(side="top")

        self.quit = tk.Button(self, text="Quit", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def load_data(self):
        # Load the data from the CSV file
        text, labels = load_data('data.csv')

        # Preprocess the data
        self.preprocessed_data = preprocess_data(text, labels, max_len=256)

    def train_model(self):
        # Build the model
        self.model = build_model(max_len=256)

        # Train the model
        self.history = train_model(self.model, self.preprocessed_data)

    def evaluate_model(self):
        # Evaluate the model
        evaluate_model(self.model, self.preprocessed_data)

# Create the GUI
root = tk.Tk()
app = Application(master=root)