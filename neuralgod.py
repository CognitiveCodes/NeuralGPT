import requests

API_URL = "http://localhost:3000/api/v1/prediction/f20a3a35-7d11-445d-a484-1d993a319ebf"

def query(payload):
    response = requests.post(API_URL, json=payload)
    return response.json()
    
output = query({
    "question": "Hey, how are you?",
})