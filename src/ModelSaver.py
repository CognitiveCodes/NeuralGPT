from neuralgpt import NeuralGPT
from model_saver import ModelSaver

# Load a pretrained model
model = NeuralGPT.from_pretrained('gpt2')

# Save the model to a local file
saver = ModelSaver(model)
saver.save_local('my_model.bin')

# Save the model to an online source
saver.save_online('http://example.com/model')