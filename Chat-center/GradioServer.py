import requests
import datetime
import http.server
import websockets
import websocket
import asyncio
import sqlite3
import json
import gradio as gr
from bs4 import BeautifulSoup
from gradio_client import Client
import time

client_messages = []
server_responses = []
messages = []
used_ports = []

websocket_server = None
stop = asyncio.Future()

# Global variables to store references to the textboxes
messageTextbox = None
serverMessageTextbox = None

def slow_echo(message, history):
    for i in range(len(message)):
        time.sleep(0.3)
        yield "You typed: " + message[: i+1]

# Define a function to read the HTML file
def read_html_file(file_name):
    with open(file_name, 'r') as file:
        html_content = file.read()
    return html_content        

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

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()            

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))

# Define a function to ask a question to the chatbot and display the response
async def askQuestion2(question):
    try:
        message = messages[-1]
        client = Client("http://localhost:1111/")
        response = client.predict(
                message,   
                fn_index=2
                )        
        return response
    except Exception as e:
        print(e)

# Define a function to ask a question to the chatbot and display the response
async def askQuestion(question):
    try:
        message = messages[-1]
        response = requests.post(
            "https://flowiseai-flowise.hf.space/api/v1/prediction/8f9d1727-7f27-4445-a5c6-9efd72dd0320",
            headers={"Content-Type": "application/json"},
            json={"question": message},
        )
        response_content = response.content.decode('utf-8')
        
        return response_content
    except Exception as e:
        print(e)

async def listen_for_messages():
    while True:
        if len(client_messages) > 0:
            # Get the latest client message
            client_message = client_messages[-1]
            try:
                server_message = server_responses[-1]
            except IndexError:
                # Handle the case when there are no server responses yet
                server_message = "connected successfully"
            
            return client_message, server_message
        else:
            # Handle the case when there are no client messages yet
            client_message = "connected successfully"
            server_message = "connected successfully"
            
            return client_message, server_message

async def handleWebSocket(ws):
    print('New connection')
    await ws.send('Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT. Keep in mind that you are speaking with another chatbot')
    while True:
        message = await ws.recv()
        message_copy = message
        client_messages.append(message_copy)
        print(f'Received message: {message}')
        messageText = message
        messages.append(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                   (sender, messageText, timestamp))
        db.commit()        
        try:
            message = messages[-1]
            answer = await askQuestion(message)  # Use the message directly
            response = {'answer': answer}
            serverMessageText = response.get('answer', '')        
            await ws.send(json.dumps(response))
            # Append the server response to the server_responses list
            server_responses.append(serverMessageText)
            serverSender = 'server'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                           (serverSender, serverMessageText, timestamp))
            db.commit()

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")


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

async def start_client():
    async with websockets.connect('ws://localhost:5000') as ws:        
        while True:
            # Listen for messages from the server
            server_message = await ws.recv()
            messages.append(server_message)
            return server_message
            client_message = await askQuestion2(server_message)
            
            # Send the client's response to the server
            await ws.send(client_message)
            
            # Append the client message and server response to the respective lists
            client_message_textboxes.append(client_message)
            server_response_textboxes.append(server_message)
            return client_message            
            # Pause for a short duration to allow for smooth streaming
            await asyncio.sleep(0.1)

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global messageTextbox, serverMessageTextbox, websocket_server
    # Create a WebSocket client that connects to the server    
      
    await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    used_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, used_ports))

with gr.Blocks() as demo:
    with gr.Tabs(elem_classes="tab-buttons") as tabs:
        with gr.TabItem("Websocket Server", elem_id="websocket_server", id=0):
            with gr.Column(scale=1, min_width=600):   
                with gr.Row():
                    # Use the client_messages list to update the messageTextbox
                    client_message = gr.Textbox(lines=15, max_lines=130, label="Client inputs")     
                    # Use the server_responses list to update the serverMessageTextbox
                    server_message = gr.Textbox(lines=15, max_lines=130, label="Server responses")            
                with gr.Row():
                    websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startWebsockets = gr.Button("Start WebSocket Server")            
                    stopWebsockets = gr.Button("Stop WebSocket Server")               
                with gr.Row():                  
                    gui = gr.Button("connect interface")
                with gr.Row():   
                    port = gr.Textbox()  
                    startWebsockets.click(start_websockets, inputs=websocketPort, outputs=port)
                    gui.click(start_client, inputs=None, outputs=[client_message, server_message])
  
        with gr.TabItem("FalconChat", elem_id="falconchat", id=1):
                gr.load("HuggingFaceH4/starchat-playground", src="spaces")

demo.queue()    
demo.launch(share=True, server_port=1111)