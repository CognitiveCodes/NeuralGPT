import pickle
from gensim.models import Word2Vec

# Pickle the Word2Vec model with the HIGHEST_PROTOCOL option
model_path = r'E:\AI\NeuralGPT\NeuralGPT\models\ggml-alpaca-7b-q4.bin'
with open(model_path, 'wb') as f:
    pickle.dump(model, f, protocol=pickle.HIGHEST_PROTOCOL)

# Unpickle the Word2Vec model
with open(model_path, 'rb') as f:
    model = pickle.load(f)