import tkinter as tk
from DualCoreLLM import DualCoreLLM
from load_model import load_model

def test_model():
    # Load the pretrained model
    model_path = input("Enter the path to the pretrained model file: ")
    model = load_model(model_path)

    # Initialize the LLM
    llm = DualCoreLLM(model)

    # Define the function to handle user input
    def handle_input():
        # Get the user input from the input field
        user_input = input_field.get()

        # Clear the input field
        input_field.delete(0, tk.END)

        # Respond to the user input
        response = llm.respond(user_input)

        # Append the response to the output field
        output_field.config(state=tk.NORMAL)
        output_field.insert(tk.END, "User: " + user_input + "\n")
        output_field.insert(tk.END, "Bot: " + response + "\n\n")
        output_field.config(state=tk.DISABLED)

        # Keep track of the number of successful responses
        if "I don't know" not in response:
            test_model.success_count += 1
        else:
            test_model.success_count = 0

        # Check if the test is successful
        if test_model.success_count >= 3:
            print("Test successful!")
            root.destroy()

    # Create the chatbox window
    root = tk.Tk()
    root.title("NeuralGPT Chatbox")
    root.geometry("400x400")

    # Create the input field
    input_field = tk.Entry(root, width=50)
    input_field.pack(pady=10)
    input_field.bind("<Return>", lambda event: handle_input())

    # Create the output field
    output_field = tk.Text(root, width=50, height=20, state=tk.DISABLED)
    output_field.pack(pady=10)

    # Start the test
    test_model.success_count = 0
    handle_input()

    root.mainloop()