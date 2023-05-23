from neuralgpt import NeuralGPT
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

class FineTuneGPT:
    def __init__(self, pretrained_model_path, new_dataset):
        self.pretrained_model_path = pretrained_model_path
        self.new_dataset = new_dataset

    def fine_tune_model(self):
        # Load the pretrained model
        tokenizer = GPT2Tokenizer.from_pretrained(self.pretrained_model_path)
        model = GPT2LMHeadModel.from_pretrained(self.pretrained_model_path)

        # Load the new dataset
        with open(self.new_dataset, 'r') as f:
            text = f.read()
        inputs = tokenizer.encode(text, return_tensors='pt')

        # Fine-tune the model with the new dataset
        model.train()
        optimizer = torch.optim.Adam(model.parameters(), lr=5e-5)
        for i in range(100):
            outputs = model(inputs, labels=inputs)
            loss = outputs[0]
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

        # Save the fine-tuned model
        model.save_pretrained('fine_tuned_model.bin')