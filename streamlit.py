import datetime
import websockets
import asyncio
import sqlite3
import json
import g4f
import streamlit as st

servers = {}
inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

websocket_server = None

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()

system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

client_message = st.text_area("Client inputs", height=15, max_chars=130)    
server_message = st.text_area("Server responses", height=15, max_chars=130)

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))

# Define the function for asking a question to the chatbot
async def askQuestion(question):
    try:
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10")
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

        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            provider=g4f.Provider.Bing,
            messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": past_user_inputs[-1]},
            {"role": "assistant", "content": generated_responses[-1]},
            {"role": "user", "content": question}
            ])
        
        st.text(response)            
        return response
            
    except Exception as e:
        st.text(e)

async def handleWebSocket(ws):    
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
    print('New connection')
    await ws.send(instruction)
    while True:
        message = await ws.recv()        
        print(f'Received message: {message}')
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, message, timestamp))
        db.commit()   
        try:
            response = await askQuestion(message)
            serverResponse = f"server: {response}"
            print(serverResponse)
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()   
            # Append the server response to the server_responses list
            await ws.send(serverResponse)
                    
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    st.text(f"Starting WebSocket server on port {websocketPort}...")
    st.text("Used ports:\n" + '\n'.join(map(str, server_ports)))
    await asyncio.Future()  
    
async def start_client(clientPort):
    global ws
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    async with websockets.connect(uri) as ws:        
        while True:
            # Listen for messages from the server            
            input_message = await ws.recv()
            outputs.append(input_message)
            output_message = await askQuestion(input_message)
            inputs.append(output_message)
            await ws.send(json.dumps(output_message))

# Stop the WebSocket server
async def stop_websockets():    
    global server
    if server:
        # Close all connections gracefully
        server.close()
        # Wait for the server to close
        server.wait_closed()
        st.text("Stopping WebSocket server...")
    else:
        st.text("WebSocket server is not running.")

# Stop the WebSocket client
async def stop_client():
    global ws
    # Close the connection with the server
    ws.close()
    st.text("Stopping WebSocket client...")

def inputMsg():
    input_msg = inputs[-1]
    return input_msg    

def outputMsg():
    output_msg = outputs[-1]
    return output_msg

async def start_interface():
    while True:
        event = st.text_input("Event")
        if event in ('Stop WebSocket client', 'sg.WIN_CLOSED'):
            break
        elif event == 'Start WebSocket server':
            websocketPort = st.slider("Websocket server port", 1000, 9999)
            await start_websockets(websocketPort)
        elif event == 'Start WebSocket client':
            clientPort = st.slider("Websocket client port", 1000, 9999)
            await start_client(clientPort)
        elif event == 'Ask the agent':
            question = st.text_input("User Input")
            await askQuestion(question)
        elif event == 'Clear Textboxes':
            inputs.clear()
            outputs.clear()
            st.text("Textboxes cleared.")
