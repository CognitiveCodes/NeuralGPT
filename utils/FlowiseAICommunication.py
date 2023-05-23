import requests
import json

class FlowiseAICommunication:
    def __init__(self, url):
        self.url = url

    def send_message(self, message):
        data = {"message": message}
        try:
            response = requests.post(self.url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def receive_message(self):
        try:
            response = requests.get(self.url)
            return response.json()["message"]
        except requests.exceptions.RequestException as e:
            print(e)
            return None