import tkinter as tk
from neuralgpt import NeuralGPT
from model_loader import ModelLoader

class ChatBox:
    def __init__(self):
        self.model = None
        self.loader = ModelLoader()

        self.root = tk.Tk()
        self.root.title('Chatbox')

        self.input_label = tk.Label(self.root, text='Input:')
        self.input_label.pack()

        self.input_field = tk.Entry(self.root)
        self.input_field.pack()

        self.output_label = tk.Label(self.root, text='Output:')
        self.output_label.pack()

        self.output_field = tk.Text(self.root, height=10, width=50)
        self.output_field.pack()

        self.submit_button = tk.Button(self.root, text='Submit', command=self.submit)
        self.submit_button.pack()

    def submit(self):
        if not self.model:
            # Load the model if it hasn't been loaded yet
            self.model = self.loader.load_local('my_model.bin')

        # Get the user input
        user_input = self.input_field.get()

        # Generate a response using the model
        response = self.model.generate(user_input)

        # Display the response in the output field
        self.output_field.insert(tk.END, response + '\n')

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    chatbox = ChatBox()
    chatbox.run()