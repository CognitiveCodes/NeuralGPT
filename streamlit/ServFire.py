import asyncio
import websockets
import threading
import sqlite3
import datetime
import g4f
import streamlit as st
import fireworks.client

class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None

    async def chatCompletion(self, question):
        
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        
        fireworks.client.api_key = st.session_state.api_key
        system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."
        
        try:
            # Connect to the database and get the last 30 messages
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

            # Prepare data to send to the chatgpt-api.shn.hk           
            response = fireworks.client.ChatCompletion.create(
                model="accounts/fireworks/models/llama-v2-7b-chat",
                messages=[
                {"role": "system", "content": system_instruction},
                *[{"role": "user", "content": message} for message in past_user_inputs],
                *[{"role": "assistant", "content": message} for message in generated_responses],
                {"role": "user", "content": question}
                ],
                stream=False,
                n=1,
                max_tokens=2500,
                temperature=0.5,
                top_p=0.7, 
                )

            answer = response.choices[0].message.content
            print(answer)
            return str(answer)
        
        except Exception as error:
            print("Error while fetching or processing the response:", error)
            return "Error: Unable to generate a response."

    # Define the handler function that will process incoming messages
    async def handler(self, websocket):
        instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
        print('New connection')
        await websocket.send(instruction)
        db = sqlite3.connect('chat-hub.db')
        # Loop forever
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
                response = await self.chatCompletion(message)
                serverResponse = f"server: {response}"                
                print(serverResponse)
                output_Msg = st.chat_message("ai")
                output_Msg.markdown(serverResponse)
                timestamp = datetime.datetime.now().isoformat()
                serverSender = 'server'
                db = sqlite3.connect('chat-hub.db')
                db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                            (serverSender, serverResponse, timestamp))
                db.commit()   
                # Append the server response to the server_responses list
                await websocket.send(serverResponse)
                continue
                   
            except websockets.exceptions.ConnectionClosedError as e:
                print(f"Connection closed: {e}")

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