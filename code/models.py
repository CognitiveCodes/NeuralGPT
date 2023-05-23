import tensorflow as tf
from tensorflow.keras.layers import Input, Embedding, Dense, Dropout, LayerNormalization, Add, Concatenate
from tensorflow.keras.models import Model

class GPTModel:
    def __init__(self, vocab_size, max_len, embedding_dim=256, num_layers=4, num_heads=8, dff=512, dropout_rate=0.1):
        self.vocab_size = vocab_size
        self.max_len = max_len
        self.embedding_dim = embedding_dim
        self.num_layers = num_layers
        self.num_heads = num_heads
        self.dff = dff
        self.dropout_rate = dropout_rate
        
        self.build_model()
        
    def build_model(self):
        # Define the input layer
        inputs = Input(shape=(self.max_len,))
        
        # Define the embedding layer
        embedding = Embedding(input_dim=self.vocab_size, output_dim=self.embedding_dim)(inputs)
        
        # Define the transformer layers
        for i in range(self.num_layers):
            # Multi-head attention layer
            attention = tf.keras.layers.MultiHeadAttention(num_heads=self.num_heads, key_dim=self.embedding_dim)(embedding, embedding)
            attention = Dropout(self.dropout_rate)(attention)
            attention = LayerNormalization(epsilon=1e-6)(Add()([embedding, attention]))
            
            # Feedforward layer
            feedforward = Dense(units=self.dff, activation='relu')(attention)
            feedforward = Dropout(self.dropout_rate)(feedforward)
            feedforward = Dense(units=self.embedding_dim)(feedforward)
            feedforward = Dropout(self.dropout_rate)(feedforward)
            feedforward = LayerNormalization(epsilon=1e-6)(Add()([attention, feedforward]))
            
            # Update the embedding layer
            embedding = feedforward
        
        # Define the output layer
        outputs = Dense(units=self.vocab_size, activation='softmax')(embedding)
        
        # Define the model
        self.model = Model(inputs=inputs, outputs=outputs)