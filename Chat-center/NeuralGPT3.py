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

chat_history = []

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
db.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    message TEXT,
    timestamp TEXT
)''')


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

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))

# Define a function to ask a question to the chatbot and display the response
async def askQuestion(question):
    try:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10')
        messages = cursor.fetchall()
        pastUserInputs = []
        generatedResponses = []
        for i, message in enumerate(messages):
            if i % 2 == 0:
                pastUserInputs.append(message[2])
            else:
                generatedResponses.append(message[2])
        response = requests.post(
            "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
            headers={
                "Content-Type": "application/json",
                "Authorization": "<HUGGINGFACE_API_TOKEN>",
            },
            json={
                "inputs": {
                    "text": question,
                    "past_user_inputs": pastUserInputs,
                    "generated_responses": generatedResponses,
                },
                "full_source": False,
            },
        )
        responseJson = response.json()
        outputText = responseJson["generated_text"]
        return outputText
    except Exception as e:
        print(e)

async def handleWebSocket(ws, path):    
    print('New connection')
    try:
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
                print("question answered")
    except Exception as e:
        print(f"Error: {e}")
 
port=5000

# Start the WebSocket server 
async def start_websockets():
    await(websockets.serve(handleWebSocket, 'localhost', port))
    print(f"Starting WebSocket server on port {port}...")

# Function to stop the WebSocket server
def stop_websockets():
    global websocket_server
    if websocket_server:
        cursor.close()
        db.close()
        websocket_server.close()
        print("WebSocket server stopped.")
    else:
        print("WebSocket server is not running.")    

with gr.Blocks() as demo:
    with gr.Row():
        websocketPort = gr.Slider(minimum=1, maximum=9999, label="Websocket server port", randomize=False)
        startWebsockets = gr.Button("start Websocket Server")
        startWebsockets.click(start_websockets)    
        stopWebsockets = gr.Button("Stop WebSocket Server")
        stopWebsockets.click(stop_websockets)
    with gr.Column(scale=1, min_width=600):
      with gr.Row():
        slider_2 = gr.Slider(minimum=10, maximum=9999, label="HTTP server port (server_port)", randomize=False)         
        severrhttp = gr.Button("start HTTP Server")
    with gr.Row():
      text2 = gr.Textbox(lines=15, max_lines=30, label="Server responses")
      text1 = gr.Textbox(lines=15, max_lines=30, label="Client inputs")
    live=True

demo.launch(server_port=8888)
