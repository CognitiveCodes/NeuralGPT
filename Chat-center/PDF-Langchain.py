import datetime
import websocket
import websockets
import asyncio
import sqlite3
import json
import requests
from gradio_client import Client
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox

client = Client("http://localhost:1112/")

inputs = []
outputs = []
used_ports = []

root = tk.Tk()
root.title("WebSocket Client")

# UI Elements
input_text = tk.Text(root, height=20, width=150)
output_text = tk.Text(root, height=20, width=150)
clear_button = tk.Button(root, text="Clear Textboxes")
port_label = tk.Label(root, text="Enter Port:")
port_entry = tk.Entry(root)
port_slider = tk.Scale(root, from_=1000, to=9999, orient=tk.HORIZONTAL, label="Websocket server port")
start_button = tk.Button(root, text="Start WebSocket client")
stop_button = tk.Button(root, text="Stop WebSocket client")
user_input = tk.Text(root, height=2, width=150)
ask_agent = tk.Button(root, text="Ask the agent") 
websocket_ports = tk.Text(root, height=1, width=150)

# UI Layout
input_text.pack()
output_text.pack()
port_label.pack()
port_entry.pack()
port_slider.pack()
start_button.pack()
stop_button.pack()
user_input.pack()
ask_agent.pack()
clear_button.pack()
websocket_ports.pack()

# Function to update the UI
def update_ui():
    root.update()

# Function to clear the textboxes
def clear_textboxes():
    input_text.delete('1.0', tk.END)
    output_text.delete('1.0', tk.END)
    user_input.delete('1.0', tk.END)

# Function to send a question to the chatbot and get the response
async def askQuestion(question):
    try:
        response = client.predict(
                "E:/Repos/documents/neuralGPTs.pdf",
                question,   # str in 'Query' Textbox component
                api_name="/predict"
        )
        return response
    except requests.exceptions.RequestException as e:
        # Handle request exceptions here
        print(f"Request failed with exception: {e}")

async def start_client(websocketPort, iface):
    uri = f'ws://localhost:{websocketPort}'
    used_ports.append(websocketPort)
    async with websockets.connect(uri) as ws:
        await handleWebSocket(ws, '/')       
    
async def handleWebSocket(ws, path):
    print('New connection')
    try:
        async for message in ws:
            print(f'Received message: {message}')
            parsedMessage = json.loads(message)
            inputMsg = {"Server: ": message}
            input_text.insert(tk.END, str(inputMsg) + '\n')
            update_ui()  # Update the UI after inserting the message
            try:
                loop = asyncio.get_event_loop()
                answer = await askQuestion(parsedMessage)
                print(answer)
                message = {"PdfQA: ": answer}
                output_text.insert(tk.END, str(message) + '\n')
                update_ui()  # Update the UI after inserting the answer                
                await ws.send(json.dumps(message))
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Connection closed: {e}")
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def get_port():
    if port_entry.get():
        return int(port_entry.get())
    else:
        return port_slider.get()        

def start_client_callback():
    websocketPort = get_port()
    websocket_ports.insert(tk.END, str(websocketPort))
    update_ui()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_client(websocketPort, None))

def stop_client_callback():
    # Add your stop client logic here
    pass

async def askAgent():
    question = user_input.get('1.0','end')
    try:
        response = await askQuestion(question)
        print(response)
        output_text.insert('1.0', str(answer))
    except Exception as e:
        print(f"Error: {e}")    

clear_button.config(command=clear_textboxes)
start_button.config(command=start_client_callback)
stop_button.config(command=stop_client_callback)
ask_agent.config(command=askAgent) 

root.mainloop()
