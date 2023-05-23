import tkinter as tk
import subprocess

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.input_label = tk.Label(self, text="Enter input text:")
        self.input_label.pack(side="top")

        self.input_text = tk.Text(self, height=10, width=50)
        self.input_text.pack(side="top")

        self.run_button = tk.Button(self)
        self.run_button["text"] = "Run NeuralGPT"
        self.run_button["command"] = self.run_neuralgpt
        self.run_button.pack(side="top")

        self.output_label = tk.Label(self, text="Output:")
        self.output_label.pack(side="top")

        self.output_text = tk.Text(self, height=10, width=50)
        self.output_text.pack(side="top")

        self.quit_button = tk.Button(self, text="Quit", fg="red",
                              command=self.master.destroy)
        self.quit_button.pack(side="bottom")

    def run_neuralgpt(self):
        input_text = self.input_text.get("1.0", "end-1c")
        output = subprocess.check_output(["python", "E:/AI/NeuralGPT/NeuralGPT/src/main.py", input_text])
        self.output_text.delete("1.0", "end")
        self.output_text.insert("1.0", output.decode())

root = tk.Tk()
app = Application(master=root)
app.mainloop()