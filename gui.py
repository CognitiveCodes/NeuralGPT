import tkinter as tk
from tkinter import filedialog
from neuralgpt import NeuralGPT

class NeuralGPT_GUI:
    def __init__(self, master):
        self.master = master
        master.title("NeuralGPT GUI")

        self.model_path = tk.StringVar()
        self.model_path.set("")

        self.model_type = tk.StringVar()
        self.model_type.set("Online")

        self.label_path = tk.Label(master, text="Model path:")
        self.label_path.pack()

        self.entry_path = tk.Entry(master, textvariable=self.model_path)
        self.entry_path.pack()

        self.button_path = tk.Button(master, text="Browse", command=self.browse_model)
        self.button_path.pack()

        self.radio_online = tk.Radiobutton(master, text="Online", variable=self.model_type, value="Online")
        self.radio_online.pack()

        self.radio_local = tk.Radiobutton(master, text="Local", variable=self.model_type, value="Local")
        self.radio_local.pack()

        self.button_load = tk.Button(master, text="Load model", command=self.load_model)
        self.button_load.pack()

        self.label_input = tk.Label(master, text="Input:")
        self.label_input.pack()

        self.entry_input = tk.Entry(master)
        self.entry_input.pack()

        self.button_send = tk.Button(master, text="Send", command=self.send_input)
        self.button_send.pack()

        self.label_output = tk.Label(master, text="Output:")
        self.label_output.pack()

        self.text_output = tk.Text(master, height=10, width=50)
        self.text_output.pack()

        self.model = None

    def browse_model(self):
        if self.model_type.get() == "Local":
            self.model_path.set(filedialog.askopenfilename(filetypes=[("Bin files", "*.bin")]))

    def load_model(self):
        if self.model_type.get() == "Online":
            self.model = NeuralGPT()
        elif self.model_type.get() == "Local":
            self.model = NeuralGPT(self.model_path.get())

    def send_input(self):
        if self.model is not None:
            input_text = self.entry_input.get()
            output_text = self.model.generate_text(input_text)
            self.text_output.insert(tk.END, f"{input_text}\n")
            self.text_output.insert(tk.END, f"{output_text}\n\n")

root = tk.Tk()
my_gui = NeuralGPT_GUI(root)
root.mainloop()