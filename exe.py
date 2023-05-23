import gensim
import tkinter as tk
from utils import preprocess_text

class GUIManager:
    def __init__(self):
        # Load pre-trained Word2Vec model
        self.word2vec_model = gensim.models.KeyedVectors.load_word2vec_format('path/to/word2vec/model.bin', binary=True)

        # Create GUI
        self.root = tk.Tk()
        self.root.title("Word Embedding Demo")

        # Create text box
        self.text_box = tk.Text(self.root, height=20, width=80)
        self.text_box.pack()

        # Create button
        self.button = tk.Button(self.root, text="Execute", command=self.execute)
        self.button.pack()

    def execute(self):
        # Get input text from text box
        input_text = self.text_box.get("1.0", "end-1c")

        # Preprocess input text
        preprocessed_text = preprocess_text(input_text)

        # Process input text using pre-trained model
        word_embeddings = []
        for word in preprocessed_text.split():
            try:
                word_embedding = self.word2vec_model[word]
                word_embeddings.append(word_embedding)
            except KeyError:
                # Ignore words that are not in the vocabulary
                pass

        # Display output in text box
        output_text = f"Word embeddings: {word_embeddings}"
        self.text_box.delete("1.0", "end")
        self.text_box.insert("1.0", output_text)

if __name__ == '__main__':
    gui_manager = GUIManager()
    gui_manager.root.mainloop()