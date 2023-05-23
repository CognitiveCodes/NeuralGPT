import tensorflow as tf
import numpy as np
import pandas as pd
from models import GPTModel
from utils import load_data, preprocess_data

# Define global variables
BATCH_SIZE = 32
EPOCHS = 10
LEARNING_RATE = 0.001

# Load and preprocess the data
data = load_data('data/dataset1/data_file1.csv')
preprocessed_data = preprocess_data(data)

# Define the model architecture
model = GPTModel(preprocessed_data.vocab_size, preprocessed_data.max_len)

# Compile the model
optimizer = tf.keras.optimizers.Adam(learning_rate=LEARNING_RATE)
model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

# Train the model
history = model.fit(preprocessed_data.x_train, preprocessed_data.y_train, 
                    batch_size=BATCH_SIZE, epochs=EPOCHS, 
                    validation_data=(preprocessed_data.x_val, preprocessed_data.y_val))

# Evaluate the model
test_loss, test_acc = model.evaluate(preprocessed_data.x_test, preprocessed_data.y_test)
print(f'Test loss: {test_loss}, Test accuracy: {test_acc}')

# Save the model
model.save('models/gpt_model.h5')