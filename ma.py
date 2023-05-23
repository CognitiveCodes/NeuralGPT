import os
import pinecone
from NeuralGPT-0.1.utils import *
from NeuralGPT-0.1.gui import run_gui

# Upload pretrained model
model_path = "E:/AI/NeuralGPT/NeuralGPT/models/ggml-model-q4_0.bin"
model_name = "ggml-model-q4_0"
pinecone.create_index(index_name=model_name, dimension=768)
pinecone.index_embeddings(index_name=model_name, embeddings_path=model_path)

# Load data
data_file1 = "database1.csv"
data_file2 = "database2.csv"
data1 = load_data(data_file1)
data2 = load_data(data_file2)

# Run GUI
run_gui(data1, data2)