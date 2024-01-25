import datetime
import websockets
import asyncio
import sqlite3
import json
import g4f
import gradio as gr

servers = {}
inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

websocket_server = None
stop = asyncio.Future()

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
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10")
        messages = cursor.fetchall()
        messages.reverse()

        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()

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
            {"role": "user", "content": question}
            ])
        
        print(response)            
        return response
            
    except Exception as e:
        print(e)

async def handleWebSocket(ws):
    print('New connection')
    await ws.send('Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT. Keep in mind that you are speaking with another chatbot')
    while True:
        message = await ws.recv()
        print(f'Received message: {message}')
        try:        
            answer = await askQuestion(message)  # Use the message directly
            await ws.send(json.dumps(answer))            

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    await asyncio.Future()  
    
async def start_client(clientPort):
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    async with websockets.connect(uri) as ws:        
        while True:
            # Listen for messages from the server            
            input_message = await ws.recv()
            output_message = await askQuestion(input_message)
            await ws.send(json.dumps(output_message))

# Stop the WebSocket server
async def stop_websockets():    
    global server
    if server:
        # Close all connections gracefully
        server.close()
        # Wait for the server to close
        await server.wait_closed()
        print("Stopping WebSocket server...")
    else:
        print("WebSocket server is not running.")

# Stop the WebSocket client
async def stop_client():
    global ws
    # Close the connection with the server
    ws.close()
    print("Stopping WebSocket client...")

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
                    userInput = gr.Textbox(label="User Input")
                with gr.Row():
                    ask_Qestion = gr.Button("Ask question")    
                with gr.Row():
                    websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startWebsockets = gr.Button("Start WebSocket Server")            
                    stopWebsockets = gr.Button("Stop WebSocket Server")
                with gr.Row():  
                    port = gr.Textbox()
                with gr.Row():
                    clientPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startClient = gr.Button("Start WebSocket client")
                    stopClient = gr.Button("Stop WebSocket client")
                with gr.Row():
                    PortInUse = gr.Textbox()
                    ask_Qestion.click(askQuestion, inputs=userInput, outputs=client_message)
                    startWebsockets.click(start_websockets, inputs=websocketPort, outputs=port)
                    startClient.click(start_client, inputs=clientPort, outputs=client_message)
                    stopWebsockets.click(stop_websockets, inputs=None, outputs=port)
                    stopClient.click(stop_client, inputs=None, outputs=PortInUse)

demo.queue()    
demo.launch(share=True, server_port=1112)