import tkinter as tk
from neuralgpt import NeuralGPT

class ChatBox:
    def __init__(self):
        self.debug_mode = False
        self.neuralgpt = NeuralGPT()

        self.root = tk.Tk()
        self.root.title("ChatBox")
        self.root.geometry("400x400")

        self.input_label = tk.Label(self.root, text="User:")
        self.input_label.pack()

        self.input_field = tk.Entry(self.root)
        self.input_field.pack()

        self.output_label = tk.Label(self.root, text="ChatBot:")
        self.output_label.pack()

        self.output_field = tk.Text(self.root)
        self.output_field.pack()

        self.debug_button = tk.Button(self.root, text="Debug Mode", command=self.toggle_debug_mode)
        self.debug_button.pack()

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

    def toggle_debug_mode(self):
        self.debug_mode = not self.debug_mode

    def send_message(self):
        user_input = self.input_field.get()
        self.input_field.delete(0, tk.END)

        try:
            response = self.neuralgpt.generate_response(user_input)
            self.output_field.insert(tk.END, f"{user_input}\n")
            self.output_field.insert(tk.END, f"{response}\n")
        except Exception as e:
            if self.debug_mode:
                print(e)
            else:
                raise e

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    chatbox = ChatBox()
    chatbox.run()