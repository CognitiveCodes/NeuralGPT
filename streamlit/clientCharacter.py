import asyncio
import websockets
import threading
import sqlite3
import streamlit as st
from PyCharacterAI import Client

# Define the websocket client class
class WebSocketClient2:
    def __init__(self, uri):
        # Initialize the uri attribute
        self.uri = uri

    # Define a function that will run the client in a separate thread
    def run(self):
        # Create a thread object
        self.thread = threading.Thread(target=self.run_client)
        # Start the thread
        self.thread.start()

    # Define a function that will run the client using asyncio
    def run_client(self):
        # Get the asyncio event loop
        loop = asyncio.new_event_loop()
        # Set the event loop as the current one
        asyncio.set_event_loop(loop)
        # Run the client until it is stopped
        loop.run_until_complete(self.client())

    # Define a coroutine that will connect to the server and exchange messages
    async def startClient(self):
        client = Client()
        await client.authenticate_with_token(st.session_state.tokenChar)
        chat = await client.create_or_continue_chat(st.session_state.character_ID)
        # Connect to the server
        async with websockets.connect(self.uri) as websocket:
            # Loop forever
            while True:
                # Listen for messages from the server
                input_message = await websocket.recv()
                print(f"Server: {input_message}")
                input_Msg = st.chat_message("assistant")
                input_Msg.markdown(input_message)
                try:
                    answer = await chat.send_message(input_message)
                    response = f"{answer.src_character_name}: {answer.text}"
                    print(response)
                    outputMsg1 = st.chat_message("ai")
                    outputMsg1.markdown(response)
                    await websocket.send(response)
                    continue  

                except websockets.ConnectionClosed:
                    print("client disconnected")
                    continue

                except Exception as e:
                    print(f"Error: {e}")
                    continue