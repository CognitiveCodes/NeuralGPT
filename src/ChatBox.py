import tkinter as tk
from NeuralGPT import NeuralGPT

class ChatBox:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.model = NeuralGPT()
        self.window = tk.Tk()
        self.window.title("Chatbox")
        self.input_text = tk.StringVar()
        self.output_text = tk.StringVar()
        self.create_widgets()
    
    def create_widgets(self):
        input_label = tk.Label(self.window, text="Input:")
        input_label.grid(row=0, column=0)
        
        input_entry = tk.Entry(self.window, textvariable=self.input_text)
        input_entry.grid(row=0, column=1)
        
        output_label = tk.Label(self.window, text="Output:")
        output_label.grid(row=1, column=0)
        
        output_entry = tk.Entry(self.window, textvariable=self.output_text)
        output_entry.grid(row=1, column=1)
        
        submit_button = tk.Button(self.window, text="Submit", command=self.process_input)
        submit_button.grid(row=2, column=1)
        
        debug_button = tk.Button(self.window, text="Debug Mode", command=self.toggle_debug_mode)
        debug_button.grid(row=3, column=1)
    
    def process_input(self):
        prompt = self.input_text.get().strip()
        if not prompt:
            self.output_text.set("Error: Please enter a valid input.")
            return
        try:
            response = self.model.generate(prompt)
            self.output_text.set(response)
        except Exception as e:
            if self.debug_mode:
                print(e)
            self.output_text.set("Error: Unable to process input. Please enter a valid input.")
    
    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode
    
    def run(self):
        self.window.mainloop()

chat_box = ChatBox()
chat_box.run()