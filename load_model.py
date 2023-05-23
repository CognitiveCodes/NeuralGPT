import urllib.request
import os
import torch
from DualCoreLLM import DualCoreLLM

def load_model(model_path, use_dualcore=False):
    if model_path.startswith("http"):
        # Load model from online file
        urllib.request.urlretrieve(model_path, "model.bin")
        model_path = "model.bin"
    
    if not os.path.exists(model_path):
        raise ValueError("Model file not found.")
    
    # Load model into memory
    model = torch.load(model_path, map_location=torch.device('cpu'))
    
    if use_dualcore:
        # Initialize DualCoreLLM with pretrained model
        dualcore = DualCoreLLM(model)
        return dualcore
    else:
        return model