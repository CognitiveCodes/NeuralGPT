import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

class PreprocessedData:
    def __init__(self, x_train, y_train, x_val, y_val, x_test, y_test, vocab_size, max_len):
        self.x_train = x_train
        self.y_train = y_train
        self.x_val = x_val
        self.y_val = y_val
        self.x_test = x_test
        self.y_test = y_test
        self.vocab_size = vocab_size
        self.max_len = max_len

def load_data(file_path):
    data = pd.read_csv(file_path)
    return data

def preprocess_data(data):
    # Tokenize the text data
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(data['text'])
    sequences = tokenizer.texts_to_sequences(data['text'])
    
    # Pad the sequences to a fixed length
    max_len = max([len(seq) for seq in sequences])
    padded_sequences = pad_sequences(sequences, maxlen=max_len, padding='post')
    
    # Split the data into train, validation, and test sets
    x_train, y_train = padded_sequences[:8000], padded_sequences[:8000]
    x_val, y_val = padded_sequences[8000:9000], padded_sequences[8000:9000]
    x_test, y_test = padded_sequences[9000:], padded_sequences[9000:]
    
    # Get the vocabulary size
    vocab_size = len(tokenizer.word_index) + 1
    
    # Return the preprocessed data
    return PreprocessedData(x_train, y_train, x_val, y_val, x_test, y_test, vocab_size, max_len)