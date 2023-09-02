import requests
import datetime
import http.server
import websockets
import asyncio
import sqlite3
import json
import asyncio
import gradio as gr
from bs4 import BeautifulSoup
from gradio_client import Client

modelPath = 'nlp-model.json'

chat_history = []

# Define a placeholder function that doesn't do anything
def placeholder_fn(input_text):
    pass

# Set up the HTTP server
class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('index.html', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()

# Create a virtual DOM
with open('index.html', 'r') as file:
    html = file.read()
    soup = BeautifulSoup(html, 'html.parser')

# Define the function for handling incoming messages
async def handleMessage(message):
    response = {'message': message.get('message')}
    try:
        question = message.get('message')
        result = await askQuestion(question)
        response['result'] = result
    except Exception as e:
        print(e)
    return response
    print(response)

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))

# Send a question to the chatbot and display the response
async def ask_question(question):
    try:
        # Prepare data for the request
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": question}]
        }
        
        # Make the request to the API
        response = requests.post("http://127.0.0.1:6969/api/conversation", json=data)
        response_data = response.json()
        generated_answer = response_data['choices'][0]['message']['content']        
        
        return generated_answer
    except Exception as e:
        print(e)
        return "Error: Unable to generate a response."

async def handleWebSocket(ws, path):    
    print('New connection')
    try:
        # Set up the SQLite database
        db = sqlite3.connect('chat-hub.db')    
        db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
        db.commit()
        await ws.send('Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT. Keep in mind that you are speaking with another chatbot')

        async for message in ws:
            print(f'Received message: {message}')
            parsedMessage = json.loads(message)
            messageText = parsedMessage.get('text', '')
            timestamp = datetime.datetime.now().isoformat()
            sender = 'client'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                       (sender, messageText, timestamp))
            db.commit()
            try:
                answer = await ask_question(parsedMessage['text'])
                response = {'answer': answer}
                await ws.send(json.dumps(response))
                serverMessageText = response.get('answer', '')
                serverSender = 'server'
                db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                               (serverSender, serverMessageText, timestamp))
                db.commit()
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Connection closed: {e}")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                print("Closing connection")
    except Exception as e:
        print(f"Error: {e}")

port=5000      
# Start the WebSocket server 
async def start_websockets():
    await(websockets.serve(handleWebSocket, 'localhost', port))
    print(f"Starting WebSocket server on port {port}...")

with gr.Blocks() as demo:

    # Define Gradio interface
    fn=placeholder_fn,  # Placeholder function
    inputs=[gr.Textbox()],
    outputs=[gr.Textbox()],
    startWebsockets = gr.Button("start Websocket Server")
    startWebsockets.click(start_websockets)
    live=True

demo.launch(server_port=8888)