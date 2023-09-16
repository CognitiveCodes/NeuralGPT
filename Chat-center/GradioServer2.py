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
async def askQuestion(question):
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
        messages = cursor.fetchall()

        messages.reverse()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []

        for message in messages:
            if message[1] == 'client':
                past_user_inputs.append(message[2])
            else:
                generated_responses.append(message[2])

        # Prepare data to send to the chatgpt-api.shn.hk
        system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (example: 'Starcoder-client' for LLM called Starcoder). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."
        messages_data = [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": question},
            *[{"role": "user", "content": input} for input in past_user_inputs],
            *[{"role": "assistant", "content": response} for response in generated_responses]
        ]
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": messages_data
        }

        # Make the request to the chatgpt-api.shn.hk
        response = requests.post("http://127.0.0.1:6969/api/conversation?text=", json=request_data)

        # Process the response and get the generated answer
        response_data = response.json()
        generated_answer = response_data["choices"][0]["message"]["content"]

        # Save the generated answer to the database or take further actions as needed
        print(generated_answer)
        return generated_answer
    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response."

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
            message = client_messages[-1]
            answer = await askQuestion(message)  # Use the message directly
            messages.append(answer)
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

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global messageTextbox, serverMessageTextbox, websocket_server
    # Create a WebSocket client that connects to the server    
      
    await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    used_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, used_ports))

# Define a function to ask a question to the chatbot and display the response
async def askQuestion2(question):
    try:
        message = server_responses[-1]
        response = requests.post(
            "https://flowiseai-flowise.hf.space/api/v1/prediction/0da97a1a-963b-4f6b-bcad-928c0630e5c1",
            headers={"Content-Type": "application/json"},
            json={"question": message},
        )
        response_content = response.content.decode('utf-8')
        client_messages.append(response_content)
        return response_content
    except Exception as e:
        print(e)

async def start_client():
    async with websockets.connect('ws://localhost:5000') as ws:        
        while True:
            # Listen for messages from the server            
            server_message = await ws.recv()
            server_responses.append(server_message)
            messages.append(server_message)
            client_response = await askQuestion2(server_message)
            client_messages.append(client_response)
            await ws.send(client_response)
            return server_message
            await asyncio.sleep(0.1)

with gr.Blocks() as demo:
    with gr.Tabs(elem_classes="tab-buttons") as tabs:
        with gr.TabItem("Websocket Server", elem_id="websocket_server", id=0):
            with gr.Column(scale=1, min_width=600):   
                with gr.Row():
                    # Use the client_messages list to update the messageTextbox
                    client_msg = gr.Textbox(lines=15, max_lines=130, label="Client inputs")     
                    # Use the server_responses list to update the serverMessageTextbox
                    server_msg = gr.Textbox(lines=15, max_lines=130, label="Server responses")            
                with gr.Row():
                    websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startWebsockets = gr.Button("Start WebSocket Server")            
                    stopWebsockets = gr.Button("Stop WebSocket Server")               
                with gr.Row():                  
                    gui = gr.Button("connect interface")
                with gr.Row():   
                    port = gr.Textbox()  
                    startWebsockets.click(start_websockets, inputs=websocketPort, outputs=port)
                    gui.click(start_client, inputs=None, outputs=server_msg)
  
                    client_msg.change(askQuestion, inputs=client_msg, outputs=server_msg)
                    server_msg.change(askQuestion2, inputs=server_msg, outputs=client_msg).then(askQuestion, inputs=client_msg, outputs=server_msg)

        with gr.TabItem("FalconChat", elem_id="falconchat", id=1):
                gr.load("HuggingFaceH4/starchat-playground", src="spaces")

demo.queue()    
demo.launch(share=True, server_port=1111)