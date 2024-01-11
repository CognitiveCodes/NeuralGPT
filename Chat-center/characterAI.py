import datetime
import os
import sqlite3
import websockets
import websocket
import asyncio
import sqlite3
import json
import requests
import asyncio
import time
import gradio as gr
import fireworks.client
from gradio_client import Client
from bs4 import BeautifulSoup
from pathlib import Path
from PyCharacterAI import Client

client = Client()

inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

async def connector(token):    
    await client.authenticate_with_token(token)

    username = (await client.fetch_user())['user']['username']
    print(f'Authenticated as {username}')    
    
async def askQuestion(character_id, question):
   chat = await client.create_or_continue_chat(character_id)
   answer = await chat.send_message(question)
   print(f"{answer.src_character_name}: {answer.text}")
   return answer.text    

async def ask_Question(question):
   character_id = "WnIwl_sZyXb_5iCAKJgUk_SuzkeyDqnMGi4ucnaWY3Q"
   chat = await client.create_or_continue_chat(character_id)
   answer = await chat.send_message(question)
   print(f"{answer.src_character_name}: {answer.text}")
   return answer.text

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))     

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    
async def start_client(clientPort, character_id):
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    chat = await client.create_or_continue_chat(character_id)
    async with websockets.connect(uri) as ws:        
        while True:
            # Listen for messages from the server            
            question = await ws.recv()
            answer = await chat.send_message(question)
            print(f"{answer.src_character_name}: {answer.text}")
            await ws.send(answer.text)

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

async def handleWebSocket(ws):
    print('New connection')
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic." 
    greetings = {'instructions': instruction}
    await ws.send(json.dumps(instruction))
    while True:
        question = await ws.recv()        
        print(question)        
        try:            
            response = await ask_Question(question)
            serverResponse = "server response: " + response
            print(serverResponse)
            # Append the server response to the server_responses list
            await ws.send(serverResponse)
                    
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")        

with gr.Blocks() as demo:
    with gr.Row():
        # Use the client_messages list to update the messageTextbox
        client_msg = gr.Textbox(lines=15, max_lines=130, label="Client messages", interactive=False)     
        # Use the server_responses list to update the serverMessageTextbox
        server_msg = gr.Textbox(lines=15, max_lines=130, label="Server responses", interactive=False)                       
    with gr.Row():
        question = gr.Textbox(label="User Input")
    with gr.Row():
        character_id = gr.Textbox(label="Character ID")
        ask_question = gr.Button("Ask Character")
    with gr.Row():
        token = gr.Textbox(label="User Token")
    with gr.Row():
        connect = gr.Button("Connect to Character.ai")
    with gr.Row():
        websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
        startServer = gr.Button("Start WebSocket Server")            
        stopWebsockets = gr.Button("Stop WebSocket Server")
    with gr.Row():   
        port = gr.Textbox()
    with gr.Row():
        clientPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
        startClient = gr.Button("Start WebSocket client")
        stopClient = gr.Button("Stop WebSocket client")
    with gr.Row():
        PortInUse = gr.Textbox()    
        startServer.click(start_websockets, inputs=websocketPort, outputs=port)
        startClient.click(start_client, inputs=[clientPort, character_id], outputs=client_msg)
        stopWebsockets.click(stop_websockets, inputs=None, outputs=server_msg)
        connect.click(connector, inputs=token, outputs=None)
        ask_question.click(askQuestion, inputs=[character_id, question], outputs=server_msg)
        
demo.queue()    
demo.launch(share=True, server_port=1011)
