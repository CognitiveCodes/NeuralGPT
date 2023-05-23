import torch
import torch.nn as nn
import torch.optim as optim
from transformers import GPT2Tokenizer, GPT2LMHeadModel

class NeuralGPT:
    def __init__(self, model_name_or_path='gpt2', device='cpu'):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name_or_path)
        self.model = GPT2LMHeadModel.from_pretrained(model_name_or_path)
        self.device = device
        self.model.to(self.device)
        self.model.eval()

    def generate_text(self, prompt='', max_length=100, temperature=1.0, top_p=0.9, top_k=0, repetition_penalty=1.0, num_return_sequences=1):
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        input_ids = input_ids.to(self.device)

        output_sequences = self.model.generate(
            input_ids=input_ids,
            max_length=max_length + len(input_ids[0]),
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            num_return_sequences=num_return_sequences,
        )

        generated_sequences = []
        for generated_sequence_idx, generated_sequence in enumerate(output_sequences):
            generated_sequence = generated_sequence.tolist()
            text = self.tokenizer.decode(generated_sequence, clean_up_tokenization_spaces=True)
            text = text[len(self.tokenizer.decode(input_ids[0], clean_up_tokenization_spaces=True)) : ]
            generated_sequences.append(text)

        return generated_sequences

    def save_text_to_file(self, text, file_path):
        with open(file_path, 'w') as f:
            f.write(text)