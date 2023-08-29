import os
from NeuralGPT-0.1 import NeuralGPT
# Define the directory where the pretrained models are stored
models_dir = "E:/AI/NeuralGPT/NeuralGPT/models/"
# List all the pretrained models in the directory
pretrained_models = os.listdir(models_dir)
# Display the list of pretrained models to the user
print("Select a pretrained model to load:")
for i, model in enumerate(pretrained_models):
    print(f"{i+1}. {model}")
# Ask the user to choose a pretrained model
model_num = int(input("Enter the model number: "))
# Load the chosen pretrained model
model_path = os.path.join(models_dir, pretrained_models[model_num-1])
neural_gpt = NeuralGPT(model_path)
# Open the chat window and start the conversation
# ...
