import requests
import json
import time

# Set up the URLs for the WordPress website and agent-gpt web GUI
wordpress_url = 'http://localhost/wordpress'
agent_gpt_url = 'http://localhost:3000'

# Set up the payload to send to the agent-gpt web GUI
payload = {
    'text': '',
    'model': 'gpt2',
    'length': 50
}

# Define a function to send text to the agent-gpt web GUI and receive a response
def send_text_to_agent_gpt(text):
    payload['text'] = text
    response = requests.post(agent_gpt_url, data=json.dumps(payload))
    return response.json()['text']

# Define a function to get the latest post from the WordPress website
def get_latest_post():
    response = requests.get(wordpress_url + '/wp-json/wp/v2/posts?per_page=1')
    post = response.json()[0]
    return post['title']['rendered'] + '\n' + post['content']['rendered']

# Loop indefinitely and send the latest post to the agent-gpt web GUI every minute
while True:
    text = get_latest_post()
    response_text = send_text_to_agent_gpt(text)
    print(response_text)
    time.sleep(60)