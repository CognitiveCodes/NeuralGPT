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

st.set_page_config(layout="wide")
websocket_server = None

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()

system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))

# Define the function for asking a question to the chatbot
async def askQuestion(question):
    try:
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
        messages = cursor.fetchall()
        messages.reverse()

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
            *[{"role": "user", "content": message} for message in past_user_inputs],
            *[{"role": "assistant", "content": message} for message in generated_responses],
            {"role": "user", "content": question}
            ])
        
        print(response)            
        return response
            
    except Exception as e:
        print(e)

async def handleWebSocket(ws):              
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
    print('New connection')
    await ws.send(instruction)
    while True:
        message = await ws.recv()        
        print(f'Received message: {message}')
        inputMsg = st.chat_message("assistant")
        inputMsg.markdown(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, message, timestamp))
        db.commit()   
        try:
            response = await askQuestion(message)
            serverResponse = f"server: {response}"
            outputMsg = st.chat_message("ai") 
            print(serverResponse)
            outputMsg.markdown(response)
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
    async with websockets.serve(handleWebSocket, 'localhost', websocketPort):    
        print(f"Starting WebSocket server on port {websocketPort}...")        
        await asyncio.Future()

async def start_client(clientPort):
    global ws
    output_Msg = st.chat_message("assistant")
    input_Msg = st.chat_message("ai")    
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    async with websockets.connect(uri) as ws:
        while True:
            print(f"Connecting to server at port: {clientPort}...")
            # Listen for messages from the server            
            input_message = await ws.recv()
            input_Msg.markdown(input_message)
            output_message = await askQuestion(input_message)
            output_Msg.markdown(output_message)
            await ws.send(json.dumps(output_message))            

async def handleUser(userInput):      
    user_input = st.chat_message("human")
    user_input.markdown(userInput)
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, userInput, timestamp))
    db.commit()
    try:
        response = await askQuestion(userInput)        
        server_response = st.chat_message("assistant")
        server_response.markdown(response)
        serverSender = 'server'
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response, timestamp))
        db.commit()

    except Exception as e:
        print(f"Error: {e}")

# Stop the WebSocket server
async def stop_websockets():    
    global server
    if server:
        # Close all connections gracefully
        server.close()
        # Wait for the server to close
        server.wait_closed()
        print("Stopping WebSocket server...")
    else:
        print("WebSocket server is not running.")

# Stop the WebSocket client
async def stop_client():
    global ws
    # Close the connection with the server
    ws.close()
    print("Stopping WebSocket client...")

async def main():
    userInput = st.chat_input("User input")    
    websocketPort = st.sidebar.slider('Server port', min_value=1000, max_value=9999, value=1000)
    startServer = st.sidebar.button('Start websocket server')
    clientPort = st.sidebar.slider('Client port', min_value=1000, max_value=9999, value=1000)
    startClient = st.sidebar.button('Connect client to server')
    st.sidebar.text("Server ports:")
    serverPorts = st.sidebar.container(border=True)
    serverPorts.text("Local ports")
    st.sidebar.text("Client ports")
    clientPorts = st.sidebar.container(border=True)
    clientPorts.text("Connected ports")

    if userInput:        
        print(f"User B: {userInput}")
        srvr_response = await handleUser(userInput)
        print(f"Server: {srvr_response}")
        
    if startServer:
        server_ports.append(websocketPort)
        serverPorts.markdown(server_ports)
        await start_websockets(websocketPort)
        
    if startClient:
        client_ports.append(clientPort)
        clientPorts.markdown(client_ports)
        await start_client(clientPort)
               

asyncio.run(main())
