import requests

def process_input(input_text):
    if not input_text:
        return "Please enter a valid input."
    
    try:
        response = requests.post("http://localhost:8000/predict", json={"text": input_text})
        if response.status_code == 200:
            return response.json()["generated_text"]
        else:
            return "Error processing input. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error processing input: {e}. Please try again."