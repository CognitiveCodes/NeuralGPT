import os
import sys
import time
import json
import threading
import queue
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from flowise import FlowiseAPI
from neuralgpt import NeuralGPT
# Load pretrained model
model_path = r"E:\AI\NeuralGPT\NeuralGPT\models\ggml-model-q4_0.bin"
neuralgpt = NeuralGPT(model_path)
# Initialize chat window
class ChatWindow(tk.Tk):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.title("NeuralGPT Chat")
        self.geometry("600x400")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.text_area = ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.input_area = tk.Entry(self, width=80)
        self.input_area.pack(side=tk.BOTTOM, fill=tk.X)
        self.input_area.bind("<Return>", self.on_input)
    def on_input(self, event):
        input_text = self.input_area.get().strip()
        if input_text:
            self.bot.process_input(input_text)
            self.input_area.delete(0, tk.END)
    def on_close(self):
        self.bot.stop()
        self.destroy()
# Handle communication with other active instances of Neural AI
class ChatBot:
    def __init__(self, neuralgpt):
        self.neuralgpt = neuralgpt
        self.flowise = FlowiseAPI()
        self.running = True
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()
    def run(self):
        while self.running:
            try:
                message = self.queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if message["type"] == "input":
                input_text = message["text"].strip()
                if input_text:
                    response = self.neuralgpt.generate_response(input_text)
                    self.flowise.send_message(response)
            elif message["type"] == "output":
                output_text = message["text"].strip()
                if output_text:
                    print("Flowise: " + output_text)
    def process_input(self, input_text):
        self.queue.put({"type": "input", "text": input_text})
    def process_output(self, output_text):
        self.queue.put({"type": "output", "text": output_text})
    def stop(self):
        self.running = False
        self.thread.join()
# Main function
def main():
    # Check for other active instances of Neural AI
    flowise = FlowiseAPI()
    if flowise.is_active("Neural AI"):
        bot = ChatBot(neuralgpt)
        chat_window = ChatWindow(bot)
        chat_window.mainloop()
    else:
        # Open chat window for user to speak with running instance
        print("No other active instances of Neural AI found. Please speak with the running instance.")
if __name__ == "__main__":
    main()