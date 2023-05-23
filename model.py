import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class GPT(nn.Module):
    def __init__(self, model_path):
        super(GPT, self).__init__()
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.model = GPT2LMHeadModel.from_pretrained(model_path)

    def forward(self, input_ids, attention_mask):
        outputs = self.model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        return logits