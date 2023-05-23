import tkinter as tk
import gensim
from transformers import AutoTokenizer, AutoModel

class GUIManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universal Embedding Framework")
        self.root.geometry("800x600")

        # Load pre-trained models
        self.word2vec_model = gensim.models.KeyedVectors.load_word2vec_format('models/ggml-alpaca-7b-q4.bin', binary=True)
        self.tokenizer = AutoTokenizer.from_pretrained('models/ggml-alpaca-7b-q4.bin')
        self.bert_model = AutoModel.from_pretrained('models/ggml-alpaca-7b-q4.bin')

        # Create menu bar
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        # Create text box
        self.text_box = tk.Text(self.root, height=20, width=80)
        self.text_box.pack()

        # Create button
        self.button = tk.Button(self.root, text="Execute", command=self.execute)
        self.button.pack()

    def execute(self):
        # Get input text from text box
        input_text = self.text_box.get("1.0", "end-1c")

        # Process input text using pre-trained models
        word_embeddings = self.word2vec_model[input_text.split()]
        encoded_input = self.tokenizer(input_text, return_tensors='pt')
        bert_output = self.bert_model(**encoded_input)

        # Display output in text box
        output_text = f"Word embeddings: {word_embeddings}\nBERT output: {bert_output}"
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", output_text)

if __name__ == '__main__':
    gui_manager = GUIManager()
    gui_manager.root.mainloop()