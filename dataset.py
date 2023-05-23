import torch
from torch.utils.data import Dataset

class TextDataset(Dataset):
    def __init__(self, data_path, seq_len):
        self.seq_len = seq_len
        self.vocab = self.build_vocab(data_path)
        self.data = self.load_data(data_path)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Get the sequence of tokens at the specified index
        seq = self.data[idx]

        # Convert the sequence to a tensor of token IDs
        tokens = [self.vocab[token] for token in seq]
        tokens = torch.tensor(tokens)

        # Split the sequence into input and target sequences
        input_seq = tokens[:-1]
        target_seq = tokens[1:]

        return input_seq, target_seq

    def build_vocab(self, data_path):
        # Build a vocabulary of unique tokens in the data
        vocab = {}
        with open(data_path, 'r') as f:
            for line in f:
                for token in line.strip().split():
                    if token not in vocab:
                        vocab[token] = len(vocab)
        return vocab

    def load_data(self, data_path):
        # Load the data from the specified file and split it into sequences
        data = []
        with open(data_path, 'r') as f:
            for line in f:
                tokens = line.strip().split()
                for i in range(0, len(tokens), self.seq_len):
                    seq = tokens[i:i+self.seq_len]
                    if len(seq) == self.seq_len:
                        data.append(seq)
        return data