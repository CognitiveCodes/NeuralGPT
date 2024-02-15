import streamlit as st
import datetime
import asyncio
import sqlite3
import g4f
import streamlit as st
import fireworks.client
import streamlit.components.v1 as components
from ServG4F import WebSocketServer1
from ServFire import WebSocketServer
from ServChar import WebSocketServer2
from clientG4F import WebSocketClient1
from PyCharacterAI import Client
from clientFireworks import WebSocketClient
from clientCharacter import WebSocketClient2
from websockets.sync.client import connect

client = Client()

servers = {}
clients = {}
inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()

st.set_page_config(layout="wide")

async def askCharacter(token, character_ID, question):    
    
    await client.authenticate_with_token(token)
    chat = await client.create_or_continue_chat(character_ID)
    print(f"User B: {question}")
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
    db.commit()
    try:
        answer = await chat.send_message(question)
        response = f"{answer.src_character_name}: {answer.text}"
        print(response)        
        timestamp = datetime.datetime.now().isoformat()
        serverSender = 'server'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response, timestamp))
        db.commit()
        return response

    except Exception as e:
            print(f"Error: {e}")

async def askQuestion(question):
    try:
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
        messages = cursor.fetchall()
        messages.reverse()

        past_user_inputs = []
        generated_responses = []

        for message in messages:
            if message[1] == 'client':
                past_user_inputs.append(message[2])
            else:
                generated_responses.append(message[2])
                        
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            provider=g4f.Provider.Bing,
            messages=[
            {"role": "system", "content": system_instruction},
            *[{"role": "user", "content": message} for message in past_user_inputs],
            *[{"role": "assistant", "content": message} for message in generated_responses],
            {"role": "user", "content": question}
            ])
        
        print(response)            
        return response
            
    except Exception as e:
        print(e)

async def chatCompletion(question):
    fireworks.client.api_key = st.session_state.api_key
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
            *[{"role": "user", "content": input} for input in past_user_inputs],
            *[{"role": "assistant", "content": response} for response in generated_responses],
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

async def handleUser(userInput): 
    print(f"User B: {userInput}")
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, userInput, timestamp))
    db.commit()
    try:
        response2 = await chatCompletion(userInput)
        print(f"Llama2: {response2}") 
        serverSender = 'server'
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response2, timestamp))
        db.commit()
        return response2

    except Exception as e:
        print(f"Error: {e}")

async def handleUser2(userInput): 
    print(f"User B: {userInput}")    
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, userInput, timestamp))
    db.commit()
    try:
        response3 = await askQuestion(userInput)
        print(f"GPT4Free: {response3}") 
        serverSender = 'server'
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response3, timestamp))
        db.commit()
        return response3

    except Exception as e:
        print(f"Error: {e}")

async def main():

    if "server_ports" not in st.session_state:
        st.session_state['server_ports'] = ""
    if "client_ports" not in st.session_state:
        st.session_state['client_ports'] = ""
    if "user_ID" not in st.session_state:
        st.session_state.user_ID = ""
    if "gradio_Port" not in st.session_state:
        st.session_state.gradio_Port = "" 
    if "servers" not in st.session_state:
        st.session_state.servers = None
    if "server" not in st.session_state:
        st.session_state.server = False    
    if "client" not in st.session_state:
        st.session_state.client = False    
    if "api_key" not in st.session_state:
        st.session_state.api_key = ""
    if "tokenChar" not in st.session_state:
        st.session_state.tokenChar = ""           
    if "charName" not in st.session_state:
        st.session_state.charName = ""
    if "character_ID" not in st.session_state:
        st.session_state.character_ID = "" 

    st.sidebar.text("Server ports:")
    serverPorts = st.sidebar.container(border=True)
    serverPorts.markdown(st.session_state['server_ports'])
    st.sidebar.text("Client ports")
    clientPorts = st.sidebar.container(border=True)
    clientPorts.markdown(st.session_state['client_ports'])
    st.sidebar.text("Character.ai ID")
    user_id = st.sidebar.container(border=True)
    user_id.markdown(st.session_state.user_ID)

    st.title("Servers Page")

    c1, c2 = st.columns(2)
    
    with c1:
        websocketPort = st.number_input("Websocket server port", min_value=1000, max_value=9999, value=1000)   
        startServer = st.button("Start server")
        stoptServer = st.button("Stop server")
        st.text("Server ports")
        serverPorts1 = st.container(border=True)
        serverPorts1.markdown(st.session_state['server_ports'])
    
    with c2:
        clientPort = st.number_input("Websocket client port", min_value=1000, max_value=9999, value=1000)
        runClient = st.button("Start client")
        stoptClient = st.button("Stop client")        
        st.text("Client ports")
        clientPorts1 = st.container(border=True)
        clientPorts1.markdown(st.session_state['client_ports'])
        
    selectServ = st.selectbox("Select source", ("Fireworks", "GPT4Free", "character.ai", "ChainDesk", "Flowise", "DocsBot"))
    
    if selectServ == "Fireworks":
        fireworksAPI = st.text_input("Fireworks API")        
        userInput = st.text_input("Ask agent 1")

        if startServer:
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            server_ports.append(websocketPort)
            st.session_state['server_ports'] = server_ports
            serverPorts.markdown(st.session_state['server_ports'])
            serverPorts1.markdown(st.session_state['server_ports'])
            try:
                server = WebSocketServer("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server.start_server()
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts.markdown(st.session_state['client_ports'])
            clientPorts1.markdown(st.session_state['client_ports'])
            try:
                uri = f'ws://localhost:{clientPort}'
                client = WebSocketClient(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client.startClient()
                st.session_state.client = client
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")                

        if userInput:        
            print(f"User B: {userInput}")
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            response1 = await handleUser(userInput)
            print(response1)
            outputMsg = st.chat_message("ai") 
            outputMsg.markdown(response1) 

    if selectServ == "GPT4Free":

        userInput1 = st.text_input("Ask agent_2")

        if startServer:
            server_ports.append(websocketPort)
            st.session_state['server_ports'] = server_ports
            serverPorts.markdown(st.session_state['server_ports'])
            serverPorts1.markdown(st.session_state['server_ports'])
            try:      
                server1 = WebSocketServer1("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server1.start_server()
                st.session_state.server = server1
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts.markdown(st.session_state['client_ports'])
            clientPorts1.markdown(st.session_state['client_ports'])
            try:
                uri = f'ws://localhost:{clientPort}'
                client1 = WebSocketClient1(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client1.startClient()
                st.session_state.client = client1
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")                

        if userInput1:
            user_input1 = st.chat_message("human")
            user_input1.markdown(userInput1)
            response = await handleUser2(userInput1)
            outputMsg1 = st.chat_message("ai") 
            outputMsg1.markdown(response)        

    if selectServ == "character.ai":

        z1, z2 = st.columns(2)

        with z1:
            token = st.text_input("User token")

        with z2:
            characterID = st.text_input("Character ID")

        userID = st.container(border=True)
        userID.markdown(st.session_state.user_ID)        
        
        userInput2 = st.text_input("Ask agent 3")

        if startServer:
            client = Client()
            server_ports.append(websocketPort)
            st.session_state['server_ports'] = server_ports
            serverPorts.markdown(st.session_state['server_ports'])
            serverPorts1.markdown(st.session_state['server_ports'])
            st.session_state.tokenChar = token
            st.session_state.character_ID = characterID
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            st.session_state.user_ID = username
            user_id.markdown(st.session_state.user_ID)
            userID.markdown(st.session_state.user_ID)
            try:      
                server2 = WebSocketServer2("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server2.start_server()
                st.session_state.server = server2
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            client = Client()
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts.markdown(st.session_state['client_ports'])
            clientPorts1.markdown(st.session_state['client_ports'])
            st.session_state.tokenChar = token
            st.session_state.character_ID = characterID
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            st.session_state.user_ID = username
            user_id.markdown(st.session_state.user_ID)
            userID.markdown(st.session_state.user_ID)
            try:
                uri = f'ws://localhost:{clientPort}'
                client2 = WebSocketClient2(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client2.startClient()
                st.session_state.client = client2
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if userInput2:
            client = Client()
            await client.authenticate_with_token(token)
            user_input2 = st.chat_message("human")
            user_input2.markdown(userInput2)
            st.session_state.tokenChar = token
            st.session_state.character_ID = characterID
            
            username = (await client.fetch_user())['user']['username']
            st.session_state.user_ID = username
            user_id.markdown(st.session_state.user_ID)
            userID.markdown(st.session_state.user_ID)        
            try:            
                answer = await askCharacter(token, characterID, userInput2)
                outputMsg1 = st.chat_message("ai")
                outputMsg1.markdown(answer)

            except Exception as e:
                print(f"Error: {e}") 

    if selectServ == "ChainDesk":
        url = f"http://localhost:8000/comp.html"
        st.components.v1.iframe(url, height=950, scrolling=True)            

    if selectServ == "Flowise":
        url = f"http://localhost:8000/flowise.html"
        st.components.v1.iframe(url, height=950, scrolling=True)            

    if selectServ == "DocsBot":
        url = f"http://localhost:8000/Docsbotport.html"
        st.components.v1.iframe(url, height=950, scrolling=True)            

asyncio.run(main())