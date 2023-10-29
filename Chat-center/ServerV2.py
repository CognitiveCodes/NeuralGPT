import requests
import datetime
import http.server
import websockets
import websocket
import asyncio
import sqlite3
import json
import openai
import gradio as gr
import os
import fireworks.client
from bs4 import BeautifulSoup
from gradio_client import Client
import time
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms.fireworks import Fireworks

GOOGLE_CSE_ID = "<paste your CSE ID here>"
GOOGLE_API_KEY = "<paste your Google API here>"
FIREWORKS_API_KEY = "<paste your Fireworks API here>"

fireworks.client.api_key = "<paste your Fireworks API (2nd one) here>"

client_messages = []
server_responses = []
messages = []

client1_msg = []
client2_msg = []
client3_msg = []

server_ports = []
client_ports = []

server = None
stop = asyncio.Future()

# Global variables to store references to the textboxes
messageTextbox = None
serverMessageTextbox = None

root = tk.Tk()
root.title("WebSocket Client")

# UI Elements
input_text = tk.Text(root, height=20, width=150)
output_text = tk.Text(root, height=20, width=150)
port_slider = tk.Scale(root, from_=1000, to=9999, orient=tk.HORIZONTAL, label="Websocket server port")
start_button = tk.Button(root, text="Start WebSocket server")
stop_button = tk.Button(root, text="Stop WebSocket server")
user_input = tk.Text(root, height=2, width=150)
ask_agent = tk.Button(root, text="Ask the agent")
websocket_ports = tk.Text(root, height=1, width=150)

# UI Layout
input_text.pack()
output_text.pack()
port_slider.pack()
start_button.pack()
stop_button.pack()
user_input.pack()
ask_agent.pack()
websocket_ports.pack()

# Function to update the UI
def update_ui():
    root.update()

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
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 40")
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
        last_msg = past_user_inputs[-1]
        last_response = generated_responses[-1]
        message = f'{{"client input: {last_msg}"}}'
        response = f'{{"server answer: {last_response}"}}'  

        response = fireworks.client.ChatCompletion.create(
            model="accounts/fireworks/models/llama-v2-7b-chat",
            messages=[
            {"role": "system", "content": system_instruction},
            *[{"role": "user", "content": message}],
            *[{"role": "assistant", "content": response}],
            {"role": "user", "content": question}
            ],
            stream=False,
            n=1,
            max_tokens=500,
            temperature=0.5,
            top_p=0.7, 
            )

        answer = response.choices[0].message.content
        print(answer)
        return json.dumps(answer)
    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response."

async def askQuestion2(question):
    try:
        response = fireworks.client.Completion.create(
            model="accounts/fireworks/models/llama-2-13b-guanaco-peft",
            prompt=question,
            stream=False,
            n=1,
            max_tokens=500,
            temperature=0.3,
            top_p=0.5, 
            )

        print(response)
        answer = response.choices[0].text
        return answer

    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response."

async def askQuestion3(question):
    url = 'https://api.docsbot.ai/teams/ZrbLG98bbxZ9EFqiPvyl/bots/oFFiXuQsakcqyEdpLvCB/chat'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'question': question,
        'full_source': False
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        responseText = response.content.decode('utf-8')     
        return responseText

    except requests.exceptions.RequestException as e:
        # Handle request exceptions here
        print(f"Request failed with exception: {e}")        

async def run_agent(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY

    llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b")
    tools = load_tools(["google-search", "llm-math"], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, return_intermediate_steps=True)

    response = agent({"input": question})
    return response["output"], response["intermediate_steps"]     
    response_content = response.content.decode('utf-8')     
    return response_content   

async def handleWebSocket(ws):
    print('New connection')
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic." 
    greetings = {'instructions': instruction}
    await ws.send(json.dumps(instruction))
    while True:
        message = await ws.recv()        
        print(message)
        client_messages.append(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                   (sender, message, timestamp))
        db.commit()
        try:           
            response = await askQuestion(message)
            serverResponse = f'server response:{response}'
            # Append the server response to the server_responses list
            server_responses.append(serverResponse)
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, serverResponse, timestamp))
            db.commit()
            await ws.send(json.dumps(serverResponse))
            return serverResponse

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

async def handle_message(message):
    print(f'Received message: {message}')
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
               (sender, message, timestamp))
    db.commit()
    try:
        userMessage = f'User B:{message}'
        response = await askQuestion(userMessage)
        serverResponse = f'server response:{response}'
        timestamp = datetime.datetime.now().isoformat()
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (serverSender, serverResponse, timestamp))
        db.commit()
        return serverResponse
    except Exception as e:
        print(f"Error: {e}")

# Define start_client function with a variable port
async def start_client(clientPort):
    uri = f'ws://localhost:{clientPort}'
    async with websockets.connect(uri, create_protocol=handleClient) as websocket:
        print("Connected to server at:", clientPort)
        client_ports.append(clientPort)
        return "Used ports:\n" + '\n'.join(map(str, client_ports))
        message = await websocket.recv()
        client1_msg.append(message)
        print(message)

async def handleClient(websocket, path):
        return client1_msg

async def connect_docsbot(docsbotPort):
    uri = f'ws://localhost:{docsbotPort}'
    async with websockets.connect(uri) as websocket:
        print("Connected to server at:", docsbotPort)
        client_ports.append(docsbotPort)
        return "Used ports:\n" + '\n'.join(map(str, client_ports))
        while True:
            inputMsg = await websocket.recv()
            client2_msg.append(inputMsg)
            print(message)
            return inputMsg

async def handleClient2(websocket, path):
        return client2_msg
        
async def connect_agent(agentPort):
    uri = f'ws://localhost:{agentPort}'
    async with websockets.connect(uri, create_protocol=handleClient3) as websocket:
        print("Connected to server at:", docsbotPort)
        client_ports.append(docsbotPort)
        return "Used ports:\n" + '\n'.join(map(str, client_ports))
        message = await websocket.recv()
        client3_msg.append(message)
        print(message)

async def handleClient3(websocket, path):
        return client3_msg

# Function to stop the WebSocket server
def stop_websockets():
    global server
    if server:
        cursor.close()
        db.close()
        server.close()
        print("WebSocket server stopped.")
    else:
        print("WebSocket server is not running.")    

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    # Create a WebSocket client that connects to the server    
      
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    await stop
    await server.close()        

with gr.Blocks() as demo:
    with gr.Tabs(elem_classes="tab-buttons") as tabs:
        with gr.TabItem("Websocket Server", elem_id="websocket_server", id=0):
            with gr.Column(scale=1, min_width=600):   
                with gr.Row():
                    # Use the client_messages list to update the messageTextbox
                    client_msg = gr.Textbox(lines=15, max_lines=130, label="Client messages", interactive=False)     
                    # Use the server_responses list to update the serverMessageTextbox
                    server_msg = gr.Textbox(lines=15, max_lines=130, label="Server responses", interactive=False)                       
                with gr.Row():
                    userInput = gr.Textbox(label="User Input")
                with gr.Row():    
                    Bot = gr.Button("Ask Server")                
                with gr.Row():
                    websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startServer = gr.Button("Start WebSocket Server")            
                    stopWebsockets = gr.Button("Stop WebSocket Server")
                with gr.Row():   
                    port = gr.Textbox()  
                    startServer.click(start_websockets, inputs=websocketPort, outputs=port)
                    stopWebsockets.click(stop_websockets, inputs=None, outputs=server_msg)
                                        
        with gr.TabItem("Llama2 13B Guanaco QLoRA GGML", elem_id="websocket_client", id=1):                   
            with gr.Column(scale=1, min_width=600):   
                with gr.Row():
                    # Use the client_messages list to update the messageTextbox
                    inputMsg1 = gr.Textbox(lines=15, max_lines=130, label="inputs", interactive=False)     
                    # Use the server_responses list to update the serverMessageTextbox
                    responseMsg1 = gr.Textbox(lines=15, max_lines=130, label="Client responses", interactive=False)
                with gr.Row():
                    userInput1 = gr.Textbox(label="User Input")
                with gr.Row():    
                    Bot1 = gr.Button("Ask Agent")
                with gr.Row():
                    clientPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startClient = gr.Button("Start WebSocket client")
                    stopClient = gr.Button("Stop WebSocket client")
                with gr.Row():
                    PortInUse = gr.Textbox()
                    startClient.click(start_client, inputs=clientPort, outputs=[PortInUse, inputMsg1]).then(askQuestion2, inputs=inputMsg1, outputs=client_msg)
                    Bot1.click(askQuestion2, inputs=userInput1, outputs=responseMsg1).then(askQuestion, inputs=responseMsg1, outputs=inputMsg1)
                    inputMsg1.change(askQuestion2, inputs=inputMsg1, outputs=client_msg)

        with gr.TabItem("Docsbot Agent (Wordpress)", elem_id="docsbot_client", id=2):                   
            with gr.Column(scale=1, min_width=600):   
                with gr.Row():
                    # Use the client_messages list to update the messageTextbox
                    inputMsg2 = gr.Textbox(lines=15, max_lines=130, label="Client inputs", interactive=False)     
                    # Use the server_responses list to update the serverMessageTextbox
                    responseMsg2 = gr.Textbox(lines=15, max_lines=130, label="Docsbot responses", interactive=False)
                with gr.Row():
                    userInput2 = gr.Textbox(label="User Input")
                with gr.Row():    
                    docsbot = gr.Button("Ask Docsbot Agent")    
                with gr.Row():
                    docsbotPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    connectClient = gr.Button("Connect Docsbot client")
                    stopDocsbot = gr.Button("Stop WebSocket client")
                with gr.Row():
                    usedPorts = gr.Textbox()
                    connectClient.click(start_client, inputs=docsbotPort, outputs=[usedPorts, responseMsg2]).then(askQuestion3, inputs=responseMsg2, outputs=inputMsg2)
                    docsbot.click(askQuestion3, inputs=userInput2, outputs=responseMsg2).then(askQuestion, inputs=responseMsg2, outputs=inputMsg2)
                    inputMsg2.change(askQuestion3, inputs=inputMsg2, outputs=client_msg)
        
        with gr.TabItem("Langchain Agent", elem_id="agent_client", id=3):                   
            with gr.Column(scale=1, min_width=600):   
                with gr.Row():
                    # Use the client_messages list to update the messageTextbox
                    inputMsg3 = gr.Textbox(lines=15, max_lines=130, label="questions", interactive=False)     
                    # Use the server_responses list to update the serverMessageTextbox
                    responseMsg3 = gr.Textbox(lines=15, max_lines=130, label="responses", interactive=False)
                with gr.Row():
                    userInput3 = gr.Textbox(label="User Input")    
                with gr.Row():    
                    agent = gr.Button("Ask Agent")    
                with gr.Row():
                    agentPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                    startAgent = gr.Button("Start WebSocket client")
                    stopAgent = gr.Button("Stop WebSocket client")
                with gr.Row():
                    agentPortInUse = gr.Textbox()
                    startAgent.click(connect_agent, inputs=agentPort, outputs=[agentPortInUse, responseMsg3]).then(run_agent, inputs=responseMsg3, outputs=client_msg)
                    agent.click(run_agent, inputs=userInput3, outputs=responseMsg3).then(askQuestion, inputs=responseMsg3, outputs=inputMsg3)
                    Bot.click(handle_message, inputs=userInput, outputs=server_msg)
                    inputMsg3.change(run_agent, inputs=inputMsg3, outputs=client_msg)
                    client_msg.change(handle_message , inputs=client_msg, outputs=server_msg)

demo.queue()    
demo.launch(share=True, server_port=1111)
