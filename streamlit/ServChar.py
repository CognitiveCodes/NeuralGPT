import asyncio
import websockets
import sqlite3
import datetime
import streamlit as st
from PyCharacterAI import Client

class WebSocketServer2:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None

    async def handler(self, websocket):
        client = Client()
        if "tokenChar" not in st.session_state:
            st.session_state.tokenChar = ""
        if "character_ID" not in st.session_state:
            st.session_state.character_ID = ""     
    
        await client.authenticate_with_token(st.session_state.tokenChar)
        char_id = st.session_state.character_ID
        chat = await client.create_or_continue_chat(char_id)
        instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
        print('New connection')
        await websocket.send(instruction)
        while True:
            # Receive a message from the client
            message = await websocket.recv()
            # Print the message
            print(f"Server received: {message}")
            input_Msg = st.chat_message("assistant")
            input_Msg.markdown(message)            
            timestamp = datetime.datetime.now().isoformat()
            sender = 'client'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (sender, message, timestamp))
            db.commit()
            try:
                answer = await chat.send_message(message)
                response = f"{answer.src_character_name}: {answer.text}"
                print(response)
                output_Msg = st.chat_message("ai")
                output_Msg.markdown(response)                
                timestamp = datetime.datetime.now().isoformat()
                serverSender = 'server'
                db = sqlite3.connect('chat-hub.db')
                db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                            (serverSender, response, timestamp))
                db.commit()
                await websocket.send(response)
                continue    

            except Exception as e:
                print(f"Error: {e}")

    async def start_server(self):
        self.server = await websockets.serve(
            self.handler,
            self.host,
            self.port
        )
        print(f"WebSocket server started at ws://{self.host}:{self.port}")

    def run_forever(self):
        asyncio.get_event_loop().run_until_complete(self.start_server())
        asyncio.get_event_loop().run_forever()

    async def stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped.")