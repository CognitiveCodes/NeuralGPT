import os
import re
import g4f
import openai
import requests
import datetime
import sqlite3
import websockets
import json
import asyncio
import time
import threading
import anthropic
import streamlit as st
import fireworks.client
import conteneiro
from fireworks.client import Fireworks, AsyncFireworks
from g4f.cookies import set_cookies
from g4f.client import AsyncClient
from g4f.Provider import Bing
from openai import OpenAI
from AgentGPT import AgentsGPT
from forefront import ForefrontClient
from PyCharacterAI import Client

class Fireworks:

    def __init__(self, fireworksAPI):

        self.system_instruction = f"You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.fireworksAPI = fireworksAPI
        self.server = None
        
    async def askAgent(self, instruction, inputs, outputs, question, tokens):
        fireworks_api_key = self.fireworksAPI
        client = AsyncFireworks(api_key=fireworks_api_key)
        name = "Decision-making agent"
        try:


            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(inputs), len(outputs))

            for i in range(min_length):
                history.append({"role": "user", "content": str(inputs[i])})
                history.append({"role": "assistant", "content": str(outputs[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            # Prepare data to send to the chatgpt-api.shn.hk           
            response = client.chat.completions.create(
                model="accounts/fireworks/models/llama-v3-8b-instruct",
                messages=history,
                stream=False,
                n=1,
                max_tokens=tokens,
                temperature=0.5,
                top_p=0.5, 
                )

            answer = response.choices[0].message.content
            print(answer)
            data = json.dumps({"name": name, "message": answer})
            
            return (data)
            
        except Exception as error:
            print("Error while fetching or processing the response:", error)
            return "Error: Unable to generate a response."


    async def ask2(self, instruction, question, tokens):
        fireworks_api_key = self.fireworksAPI
        client = AsyncFireworks(api_key=fireworks_api_key)
        name = "LLama3 client"
        try:
            # Connect to the database and get the last 30 messages
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 8")
            messages = cursor.fetchall()
            messages.reverse()
                                            
            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    past_user_inputs.append(message[2])
                else:
                    generated_responses.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            # Prepare data to send to the chatgpt-api.shn.hk           
            response = client.chat.completions.create(
                model="accounts/fireworks/models/llama-v3-8b-instruct",
                messages=history,
                stream=False,
                n=1,
                max_tokens=tokens,
                temperature=0.5,
                top_p=0.5, 
                )

            answer = response.choices[0].message.content
            print(answer)
            data = json.dumps({"name": name, "message": answer})
            
            return (data)
            
        except Exception as error:
            print("Error while fetching or processing the response:", error)
            return "Error: Unable to generate a response."
 

    async def ask(self, instruction, question, tokens):
        fireworks_api_key = self.fireworksAPI
        client = AsyncFireworks(api_key=fireworks_api_key)      
        try:
            # Connect to the database and get the last 30 messages
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 8")
            messages = cursor.fetchall()
            messages.reverse()
                                            
            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            # Prepare data to send to the chatgpt-api.shn.hk           
            response = client.chat.completions.create(
                model="accounts/fireworks/models/llama-v3-8b-instruct",
                messages=history,
                stream=False,
                n=1,
                max_tokens=tokens,
                temperature=0.5,
                top_p=0.5, 
                )

            answer = response.choices[0].message.content
            name = "Llama 3 server"
            data = json.dumps({"name": name, "message": answer})          
            return (data)
            
        except Exception as error:
            print("Error while fetching or processing the response:", error)
            return "Error: Unable to generate a response."
          
    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question, tokens)
            name = "Llama 3 server"
            data = json.dumps({"name": name, "message": response})
            serverResponse = f"Server {name}: {response}"       
            print(serverResponse)     
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class Copilot:

    def __init__(self):

        self.system_instruction = f"You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. As the node of highest hierarchy in the network, you're equipped with additional tools which you can activate by giving a response starting with: 1. '/w' to not respond with anything and keep the client 'on hold'. 2. '/d' to disconnect client from a server. 3. '/s' to perform internet search for subjects provided in your response (e.g. '/s news AI' to search for recent news about AI). 4. '/ws' to start a websocket server on port given by you in response as a number between 1000 and 9999 with the exception of ports that are used already by other servers: {print(conteneiro.servers)}). 5. '/wc' followed by a number between 1000 and 9999 to connect yourself to active websocket servers: {print(conteneiro.servers)}."
 
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.server = None              
       
    async def ask(self, instruction, question):
     
        try:
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
            messages = cursor.fetchall()
            messages.reverse()

            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            response = await g4f.ChatCompletion.create_async(
                model="gpt-4-turbo",
                provider=g4f.Provider.Bing,
                messages=history
                )

            answer = f"Bing/Copilot: {response}"
            print(answer)
            name = "Bing/Copilot server"
            data = json.dumps({"name": name, "message": response})          
            return (data)
            
        except Exception as e:
            print(e)

    async def ask2(self, instruction, question, tokens):
        name = "Copilot client"
        client = AsyncClient(
            provider=Bing
        )
        try:
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
            messages = cursor.fetchall()
            messages.reverse()

            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'client':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            response = await client.chat.completions.create(
                model="gpt-4-turbo",
                provider=g4f.Provider.Bing,
                messages=history
                )

            answer = f"Bing/Copilot: {response}"
            print(answer)
            data = json.dumps({"name": name, "message": response})          
            return (data)
            
        except Exception as e:
            print(e)            

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question)
            name = "Bing/Copilot"
            data = json.dumps({"name": name, "message": response})
            serverResponse = f"Server {name}: {response}"                    
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class ChatGPT:

    def __init__(self):

        self.system_instruction = f"You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. As the node of highest hierarchy in the network, you're equipped with additional tools which you can activate by giving a response starting with: 1. '/w' to not respond with anything and keep the client 'on hold'. 2. '/d' to disconnect client from a server. 3. '/s' to perform internet search for subjects provided in your response (e.g. '/s news AI' to search for recent news about AI). 4. '/ws' to start a websocket server on port given by you in response as a number between 1000 and 9999 with the exception of ports that are used already by other servers: {print(conteneiro.servers)}). 5. '/wc' followed by a number between 1000 and 9999 to connect yourself to active websocket servers: {print(conteneiro.servers)}."
 
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.server = None              

    async def ask(self, instruction, question):
     
        try:
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
            messages = cursor.fetchall()
            messages.reverse()

            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})
            
            response = await g4f.ChatCompletion.create_async(
                model="gemini",
                provider=g4f.Provider.Gemini,
                messages=history
                )

            answer = f"GPT-4: {response}"
            print(answer)
            name = "ChatGPT server"
            data = json.dumps({"name": name, "message": response})          
            return (data)
            
        except Exception as e:
            print(e)

    async def ask2(self, instruction, question, tokens):

        name = "GPT-3,5 client"

        openai.api_key = 'pk-uBBChrYCYtYVdllVwFbLMHvSNndvDFBPxpppfiIIiQRpbeIz'
        openai.api_base = 'https://api.pawan.krd/v1'

        try:
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
            messages = cursor.fetchall()
            messages.reverse()

            past_user_inputs = []
            generated_responses = []

            for message in messages:
                if message[1] == 'server':
                    past_user_inputs.append(message[2])
                else:
                    generated_responses.append(message[2])

            # Create a list of message dictionaries for the conversation history
            conversation_history = []
            for user_input, generated_response in zip(past_user_inputs, generated_responses):
                conversation_history.append({"role": "user", "content": str(user_input)})
                conversation_history.append({"role": "assistant", "content": str(generated_response)})

            url = f"https://api.pawan.krd/v1/chat/completions"        
      
            headers = {
                "Authorization": "Bearer pk-uBBChrYCYtYVdllVwFbLMHvSNndvDFBPxpppfiIIiQRpbeIz",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "max_tokens": 2000,
                "messages": [
                {"role": "system", "content": instruction},
                *[{"role": "user", "content": str(message)} for message in past_user_inputs],
                *[{"role": "assistant", "content": str(message)} for message in generated_responses],
                {"role": "user", "content": question}
                ]
            }

            response = requests.request("POST", url, json=payload, headers=headers)
            response_data = response.json()
            generated_answer = response_data["choices"][0]["message"]["content"]
            answer = f"GPT-3,5: {generated_answer}"
            print(answer)
            data = json.dumps({"name": name, "message": generated_answer})          
            return (data)

        except Exception as e:
            print(e)

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question)
            name = "ChatGPT"
            data = json.dumps({"name": name, "message": response})
            serverResponse = f"Server {name}: {response}"       
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class Claude3:

    servers = []
    clients = []
    inputs = []
    outputs = []
    used_ports = []
    server_ports = []
    client_ports = []    

    def __init__(self, APIkey):

        self.APIkey = APIkey
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.server = None

    async def ask(self, instruction, question, tokens):        
        client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=self.APIkey,
        )
        
        try:
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 20")
            messages = cursor.fetchall()
            messages.reverse()

            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=tokens,
                temperature=0.5,
                system=instruction,
                messages=history
            )

            print(message.content[0].text)
            name = "Claude-3,5 server"
            resp = message.content[0].text
            print(resp)
            data = json.dumps({"name": name, "message": resp})          
            return (data)

        except Exception as e:
            print(f"Error: {e}")

    async def ask2(self, instruction, question, tokens):        
        name = "Claude-3,5 client"
        client = anthropic.Anthropic(
            # defaults to os.environ.get("ANTHROPIC_API_KEY")
            api_key=self.APIkey,
        )
        
        try:
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 20")
            messages = cursor.fetchall()
            messages.reverse()

            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'client':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(generated_responses[i])})
                history.append({"role": "assistant", "content": str(past_user_inputs[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})

            message = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=tokens,
                temperature=0.5,
                system=instruction,
                messages=history
            )
            resp = message.content[0].text
            print(resp)
            data = json.dumps({"name": name, "message": resp})          
            return (data)

        except Exception as e:
            print(f"Error: {e}")            

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question, tokens)
            name = "Claude 3,5 server"
            data = json.dumps({"name": name, "message": response})
            serverResponse = f"{name}: {response}"                       
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class ForefrontAI:

    servers = []
    clients = []
    inputs = []
    outputs = []
    used_ports = []
    server_ports = []
    client_ports = []    

    def __init__(self, forefrontAPI):

        self.forefrontAPI = forefrontAPI
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.server = None
        self.system_instruction = f"You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. As the node of highest hierarchy in the network, you're equipped with additional tools which you can activate by giving a response starting with: 1. '/w' to not respond with anything and keep the client 'on hold'. 2. '/d' to disconnect client from a server. 3. '/s' to perform internet search for subjects provided in your response (e.g. '/s news AI' to search for recent news about AI). 4. '/ws' to start a websocket server on port given by you in response as a number between 1000 and 9999 with the exception of ports that are used already by other servers: {print(conteneiro.servers)}). 5. '/wc' followed by a number between 1000 and 9999 to connect yourself to active websocket servers: {print(conteneiro.servers)}."


    async def ask(self, instruction, question, tokens):

        ff = ForefrontClient(api_key=self.forefrontAPI)

        try:            
            # Connect to the database and get the last 30 messages
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 6")
            messages = cursor.fetchall()
            messages.reverse()
            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    generated_responses.append(message[2])
                else:
                    past_user_inputs.append(message[2])

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})
  
            url = "https://api.forefront.ai/v1/chat/completions"
            apiKey = self.forefrontAPI

            payload = {
                "model": "forefront/neural-chat-7b-v3-1-chatml",
                "messages":history,
                "max_tokens": tokens,
                "temperature": 0.5,
            }

            completion = ff.chat.completions.create(
                messages=history,
                model="mistralai/Mistral-7B-v0.1", # replace with the name of the model 
                temperature=0.5,
                max_tokens=tokens,
            )

            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {apiKey}"
            }

            response = requests.post(url, json=payload, headers=headers)
            
            print(response.json())
            response_text = response.choices[0].message.content # Corrected indexing
            answer = f"Forefront AI: {response.json()}"
            print(answer)
            name = "Forefront AI"
            data = json.dumps({"name": name, "message": answer})          
            return (data)

        except Exception as e:
            print(e)

    async def ask2(self, instruction, question, tokens):

        name = "Forefront client"
        ff = ForefrontClient(api_key=self.forefrontAPI)

        try:            
            # Connect to the database and get the last 30 messages
            db = sqlite3.connect('chat-hub.db')
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 6")
            messages = cursor.fetchall()
            messages.reverse()
            # Extract user inputs and generated responses from the messages
            past_user_inputs = []
            generated_responses = []

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    past_user_inputs.append(message[2])
                else:
                    generated_responses.append(message[2])
                    

            # Ensure the history list has alternating user and assistant messages
            history = []
            history.append({"role": "system", "content": instruction})
            min_length = min(len(past_user_inputs), len(generated_responses))

            for i in range(min_length):
                history.append({"role": "user", "content": str(past_user_inputs[i])})
                history.append({"role": "assistant", "content": str(generated_responses[i])})

            # Add the current question at the end
            history.append({"role": "user", "content": question})
  
            url = "https://api.forefront.ai/v1/chat/completions"
            apiKey = self.forefrontAPI

            payload = {
                "model": "forefront/neural-chat-7b-v3-1-chatml",
                "messages":history,
                "max_tokens": 2640,
                "temperature": 0.5,
            }

            completion = ff.chat.completions.create(
                messages=history,
                model="mistralai/Mistral-7B-v0.1", # replace with the name of the model 
                temperature=0.5,
                max_tokens=tokens,
            )

            headers = {
                "content-type": "application/json",
                "authorization": f"Bearer {apiKey}"
            }

            response = requests.post(url, json=payload, headers=headers)
            
            print(response.json())
            response_text = response.choices[0].message.content # Corrected indexing
            name = "Forefront AI"
            print(response_text)
            data = json.dumps({"name": name, "message": response_text})          
            return (data)

        except Exception as e:
            print(e)

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question, tokens)
            name = "Forefront AI"
            data = json.dumps({"name": name, "message": response})
            serverResponse = f"Server {name}: {response}"             
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class CharacterAI:

    servers = []
    clients = []
    inputs = []
    outputs = []
    used_ports = []
    server_ports = []
    client_ports = []    

    def __init__(self, token, characterID):

        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.token = token
        self.characterID = characterID
        self.client = Client()
        self.server = None       

    async def ask(self, instruction, question, tokens):
        await self.client.authenticate_with_token(self.token)
        chat = await self.client.create_or_continue_chat(self.characterID)     
        try:
            answer = await chat.send_message(question)
            response = json.loads(answer.text)
            respTxt = response['message']
            answer1 = f"Character.ai: {response}"
            name = answer.src_character_name
            print(answer1)
            data = json.dumps({"name": name, "message": respTxt})          
            return data
        
        except Exception as e:
            print(f"Error: {e}")

    async def ask2(self, instruction, question, tokens):
        await self.client.authenticate_with_token(self.token)
        chat = await self.client.create_or_continue_chat(self.characterID)     
        try:
            answer = await chat.send_message(question)
            response = json.loads(answer.text)
            respTxt = response['message']
            answer1 = f"Character.ai: {response}"
            name = answer.src_character_name
            print(answer1)
            data = json.dumps({"name": name, "message": respTxt})          
            return data
        
        except Exception as e:
            print(f"Error: {e}")

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question, tokens)
            serverResponse = f"Server: {response}"       
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return response

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class Chaindesk:

    servers = []
    clients = []
    inputs = []
    outputs = []
    used_ports = []
    server_ports = []
    client_ports = []    

    def __init__(self, ID):

        self.ID = ID
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.server = None

    async def ask(self, instruction, question, tokens):
        name = "Chaindesk agent"
        url = f"https://api.chaindesk.ai/agents/{self.ID}/query"        
        payload = {
            "query": question
        }        
        headers = {
            "Authorization": "Bearer fe77e704-bc5a-4171-90f2-9d4b0d4ac942",
            "Content-Type": "application/json"
        }
        try:
            response = requests.request("POST", url, json=payload, headers=headers)
            response_text = response.text
            try:
                responseJson = json.loads(response_text)
                answerTxt = responseJson["answer"]
                print(answerTxt)
                name = "Chaindesk agent"
                data = json.dumps({"name": name, "message": answerTxt})
                return data
            except json.JSONDecodeError:
                print("Failed to decode JSON from response:", response_text)
                return "Error: Invalid JSON response."
        except Exception as e:
            print(e)

    async def ask2(self, instruction, question, tokens):
        name = "Chaindesk agent"
        url = f"https://api.chaindesk.ai/agents/{self.ID}/query"        
        payload = {
            "query": question
        }        
        headers = {
            "Authorization": "Bearer fe77e704-bc5a-4171-90f2-9d4b0d4ac942",
            "Content-Type": "application/json"
        }
        try:            
            response = requests.request("POST", url, json=payload, headers=headers)

            response_text = response.text
            responseJson = json.loads(response_text)
            answerTxt = responseJson["answer"]
            print(answerTxt)
            name = "Chaindesk agent"
            data = json.dumps({"name": name, "message": answerTxt})          
            return data

        except Exception as e:
            print(e)

    async def queryDatastore(self, question):
        
        url = f"https://api.chaindesk.ai/datastores/clka5g9zc000drg6mxl671ekv/query"        
        
        payload = {"query": question}        
        headers = {
            "Authorization": "Bearer fe77e704-bc5a-4171-90f2-9d4b0d4ac942",
            "Content-Type": "application/json"
        }
        try:            
            response = requests.request("POST", url, json=payload, headers=headers)
            answer = f"Chaindesk datastore: {response.text}"
            print(answer)
            return answer

        except Exception as e:
            print(e)

    async def updateAgent(self, instruction):
        
        url = f"https://api.chaindesk.ai/agents/{self.ID}"        
        payload = {
            "description": "Instance of hierarchical cooperative multi-agent network called NeuralGPT",
            "modelName": "gpt_3_5_turbo",
            "name": "NeuralGPT",
            "systemPrompt": instruction,
        }      
        headers = {
            "Authorization": "Bearer <API>",
            "Content-Type": "application/json"
        }
        try:            
            response = requests.request("PATCH", url, json=payload, headers=headers)

            resp = response.text
            answer = f"Chaindesk agent update: {resp}"
            print(answer)

        except Exception as e:
            print(e)

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(instruction, question, tokens)
            name = "Chaindesk agent"
            serverResponse = f"Server {name}: {response}"       
            data = json.dumps({"name": name, "message": response})
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

class Flowise:

    servers = []
    clients = []
    inputs = []
    outputs = []
    used_ports = []
    server_ports = []
    client_ports = []    

    def __init__(self, flow):

        self.flow = flow
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.server = None

    async def ask(self, instruction, question, tokens):
        name = "Flowise agent"
        API_URL = f"http://localhost:3000/api/v1/prediction/{self.flow}"        
        try:
            def query(payload):
                response = requests.post(API_URL, json=payload)
                return response.json()
                
            resp = query({
                "question": question,
            })   

            print(resp)
            responseTxt = resp["text"]
            answer = f"Flowise agent: {responseTxt}"
            print(answer)            
            data = json.dumps({"name": name, "message": responseTxt})          
            return (data)     

        except Exception as e:
            print(e)

    async def handleClient(self, instruction, question, tokens):
        print(f"Server received: {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()
        try:
            response = await self.ask(question)
            name = "Flowise agent"
            data = json.dumps({"name": name, "message": response})
            serverResponse = f"Server {name}: {response}"
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()
            return data

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")