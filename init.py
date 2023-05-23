from neuralgpt import NeuralGPT
from DualCoreLLM import DualCoreLLM
import tkinter as tk

def load_model(model_path):
    # Load pretrained model
    model = NeuralGPT(device='cpu')
    model.model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    return model

def generate_response(prompt, model, coherence_checker):
    # Generate response
    response = model.generate_text(prompt=prompt, max_length=50, temperature=0.7, top_p=0.9, top_k=0, repetition_penalty=1.0, num_return_sequences=1)[0]

    # Check coherence and grammar
    if coherence_checker.check_coherence(response) and coherence_checker.check_grammar(response):
        return response
    else:
        return generate_response(prompt, model, coherence_checker)

def main():
    # Load pretrained model
    model_path = 'path/to/model.bin'
    model = load_model(model_path)

    # Initialize coherence checker
    coherence_checker = DualCoreLLM()

    # Initialize GUI
    root = tk.Tk()
    root.title('NeuralGPT Chatbot')
    root.geometry('400x400')

    # Create input/output fields
    input_field = tk.Entry(root, width=50)
    input_field.pack(pady=10)

    output_field = tk.Text(root, height=20, width=50)
    output_field.pack(pady=10)

    # Define response function
    def respond():
        prompt = input_field.get()
        response = generate_response(prompt, model, coherence_checker)
        output_field.insert(tk.END, 'User: ' + prompt + '\n')
        output_field.insert(tk.END, 'Chatbot: ' + response + '\n\n')
        model.save_text_to_file(response, 'generated_text.txt')

    # Create response button
    response_button = tk.Button(root, text='Respond', command=respond)
    response_button.pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()