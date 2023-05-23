from model import GPT
import torch

# Set the device to use
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the GPT model
model_path = 'E:/AI/NeuralGPT/NeuralGPT/models/ggml-model-q4_0.bin'
model = GPT(model_path)
model.to(device)

# Set the model to evaluation mode
model.eval()

# Get user input
prompt = input('Enter a prompt: ')

# Generate text based on the user input
generated_text = ''
while not generated_text:
    # Tokenize the prompt and generate the input sequence
    input_ids = model.tokenizer.encode(prompt, return_tensors='pt').to(device)

    # Generate the output sequence
    max_length = len(input_ids.flatten()) + 50
    output = model.model.generate(input_ids=input_ids, max_length=max_length, do_sample=True)

    # Decode the output sequence and remove the prompt
    generated_text = model.tokenizer.decode(output[0], skip_special_tokens=True)
    generated_text = generated_text[len(prompt):].strip()

# Print the generated text
print(generated_text)