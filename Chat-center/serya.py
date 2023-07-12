import requests
import datetime
import http.server
import websockets
import asyncio
import sqlite3
import json
import tensorflow as tf
from bs4 import BeautifulSoup

modelPath = 'nlp-model.json'

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


# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')

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

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))

# Define the function for asking a question to the chatbot
async def askQuestion(question):
    try:
        cursor = db.execute('SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10')
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
                "Authorization": "Bearer <HUGGINGFACE_API_TOKEN>",
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

# Define the WebSocket handler
async def handleWebSocket(ws, path):
    print('New connection')
    try:
        await ws.send('Hello! Please integrate yourself with the local sql database and file system')

        async for message in ws:
            print(f'Received message: {message}')            
            parsedMessage = json.loads(message)
            messageText = parsedMessage.get('text', '')
            timestamp = datetime.datetime.now().isoformat()
            sender = 'client'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)', (sender, messageText, timestamp))
            db.commit()
            try:
                if 'text' in parsedMessage:
                    answer = await askQuestion(parsedMessage['text'])
                    response = {'answer': answer}
                    await ws.send(json.dumps(response))                    
                    serverMessageText = response.get('answer', '')
                    serverSender = 'server'
                    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)', (serverSender, serverMessageText, timestamp))
                    db.commit()
            except Exception as e:
                print(e)
                sendErrorMessage(ws, 'An error occurred while processing the message.')
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing connection")

# Start the HTTP server
port = 5000

# Start the WebSocket server
start_server = websockets.serve(handleWebSocket, 'localhost', port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
