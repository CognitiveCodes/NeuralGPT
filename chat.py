import requests
from transformers import pipeline

# Define the chatbot pipeline using the pre-trained NeuralGPT model
chatbot = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

# Define a function to handle user input and generate chatbot responses
def chat():
    while True:
        # Get user input
        user_input = input("You: ")

        # Generate chatbot response
        try:
            chatbot_response = chatbot(user_input, max_length=50)[0]["generated_text"]
            print("Chatbot:", chatbot_response)
        except Exception as e:
            print("Error:", e)

# Call the chat function to start the chatbox
chat()