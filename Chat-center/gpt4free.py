import requests
import g4f
import datetime
import http.server
import websockets
import asyncio
import sqlite3
import json
import asyncio
from bs4 import BeautifulSoup
from gradio_client import Client

modelPath = 'nlp-model.json'

chat_history = []


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
    print(response)

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
        response = g4f.ChatCompletion.create(model=g4f.Model.gpt_4, messages=[
                                     {"role": "user", "content": pastUserInputs,
				     "role": "assistant", "content": generatedResponse}]) 
        print(response)            
        return response        
    except Exception as e:
        print(e)

async def handleWebSocket(ws, path):
    print('New connection')
    try:
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
                if 'text' in parsedMessage:
                    loop = asyncio.get_event_loop()
                    answer = await loop.run_in_executor(None, askQuestion, parsedMessage['text'])
                    answer_result = await answer  # Await the coroutine
                    response = {'answer': answer_result}
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
                print("Closing connection")
    except Exception as e:
        print(f"Error: {e}")


port=5000      
# Start the WebSocket server
start_server = websockets.serve(handleWebSocket, 'localhost', port)
print(f"Starting WebSocket server on port {port}...")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
