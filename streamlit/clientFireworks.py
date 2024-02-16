import asyncio
import websockets
import threading
import sqlite3
import fireworks.client
import streamlit as st

# Define the websocket client class
class WebSocketClient:
    def __init__(self, uri):
        # Initialize the uri attribute
        self.uri = uri

    async def chatCompletion(self, question):
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
                if message[1] == 'server':
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
                    response = await self.chatCompletion(input_message)
                    res1 = f"Client: {response}"
                    output_Msg = st.chat_message("ai")
                    output_Msg.markdown(res1)
                    await websocket.send(res1)

                except websockets.ConnectionClosed:
                    print("client disconnected")
                    continue

                except Exception as e:
                    print(f"Error: {e}")
                    continue