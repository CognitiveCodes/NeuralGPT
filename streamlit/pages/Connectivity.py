import streamlit as st
import datetime
import asyncio
import sqlite3
import g4f
import http.server
import socketserver
import streamlit as st
import fireworks.client
import streamlit.components.v1 as components
from ServG4F import WebSocketServer1
from ServG4F2 import WebSocketServer3
from ServFire import WebSocketServer
from ServChar import WebSocketServer2
from clientG4F import WebSocketClient1
from forefront import ForefrontClient
from clientG4F2 import WebSocketClient3
from ServForefront import WebSocketServer4
from PyCharacterAI import Client
from clientForefront import WebSocketClient4
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

async def askQuestion2(question):
    system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."
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
            model="gpt-3.5-turbo",
            provider=g4f.Provider.You,
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

async def askQuestion3(question):
    forefront_API = st.session_state.forefront_api
    ff = ForefrontClient(api_key=forefront_API)
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 3")
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

        last_msg = past_user_inputs[-1]
        last_response = generated_responses[-1]
        message = f'{{"client input: {last_msg}"}}'
        response = f'{{"server answer: {last_response}"}}' 

        # Construct the message sequence for the chat model
        response = ff.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                *[{"role": "user", "content": past_user_inputs[-1]}],
                *[{"role": "assistant", "content": generated_responses[-1]}],
                {"role": "user", "content": question}
            ],
            stream=False,
            model="forefront/neural-chat-7b-v3-1-chatml",  # Replace with the actual model name
            temperature=0.5,
            max_tokens=500,
        )
        
        response_text = response.choices[0].message # Corrected indexing

        print("Extracted message text:", response_text)
        return response_text

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
        print(response)
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
        print(f"Bing: {response3}") 
        serverSender = 'server'
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response3, timestamp))
        db.commit()
        return response3

    except Exception as e:
        print(f"Error: {e}")

async def handleUser3(userInput): 
    print(f"User B: {userInput}")    
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, userInput, timestamp))
    db.commit()
    try:
        response3 = await askQuestion2(userInput)
        print(f"GPT-3,5: {response3}") 
        serverSender = 'server'
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response3, timestamp))
        db.commit()
        return response3

    except Exception as e:
        print(f"Error: {e}")

async def handleUser4(userInput): 
    print(f"User B: {userInput}")
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, userInput, timestamp))
    db.commit()
    try:
        response2 = await askQuestion3(userInput)
        print(f"Firefront: {response2}") 
        serverSender = 'server'
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, response2, timestamp))
        db.commit()
        return response2

    except Exception as e:
        print(f"Error: {e}")        

# Stop the WebSocket server
async def stop_websockets():    
    global server
    if server:
        # Close all connections gracefully
        await server.close()
        # Wait for the server to close
        await server.wait_closed()
        print("Stopping WebSocket server...")
    else:
        print("WebSocket server is not running.")

# Stop the WebSocket client
async def stop_client():
    global ws
    # Close the connection with the server
    await ws.close()
    print("Stopping WebSocket client...")

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
    if "forefront_api" not in st.session_state:
        st.session_state.forefront_api = ""    
    if "tokenChar" not in st.session_state:
        st.session_state.tokenChar = ""           
    if "charName" not in st.session_state:
        st.session_state.charName = ""
    if "character_ID" not in st.session_state:
        st.session_state.character_ID = "" 
    
    if "http_server" not in st.session_state:
        
        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        st.session_state.http_server = True

        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("serving at port", PORT)
            httpd.serve_forever()

    st.title("Servers Page")

    selectServ = st.selectbox("Select source", ("Fireworks", "Bing", "GPT-3,5", "character.ai", "Forefront", "ChainDesk", "Flowise", "DocsBot"))

    c1, c2 = st.columns(2)
    
    with c1:
        websocketPort = st.number_input("Websocket server port", min_value=1000, max_value=9999, value=1000)   
        startServer = st.button("Start server")
        stopServer = st.button("Stop server")
        st.text("Server ports")
        serverPorts1 = st.container(border=True)
        serverPorts1.markdown(st.session_state['server_ports'])
    
    with c2:
        clientPort = st.number_input("Websocket client port", min_value=1000, max_value=9999, value=1000)
        runClient = st.button("Start client")
        stopClient = st.button("Stop client")        
        st.text("Client ports")
        clientPorts1 = st.container(border=True)
        clientPorts1.markdown(st.session_state['client_ports'])

    with st.sidebar:
        # Wyświetlanie danych, które mogą być modyfikowane na różnych stronach
        serverPorts = st.container(border=True)
        serverPorts.markdown(st.session_state['server_ports'])
        st.text("Client ports")
        clientPorts = st.container(border=True)
        clientPorts.markdown(st.session_state['client_ports'])
        st.text("Character.ai ID")
        user_id = st.container(border=True)
        user_id.markdown(st.session_state.user_ID)    
        status = st.status(label="runs", state="complete", expanded=False)

        if st.session_state.server == True:
            st.markdown("server running...")
        
        if st.session_state.client == True:    
            st.markdown("client running")    
   
    if stopServer:
        stop_websockets

    if stopClient:
        stop_client   
    
    if selectServ == "Fireworks":
        fireworksAPI = st.text_input("Fireworks API")        
        userInput = st.text_input("Ask agent 1")

        if startServer:
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            server_ports.append(websocketPort)
            st.session_state.server = True
            st.session_state['server_ports'] = server_ports
            serverPorts1.markdown(st.session_state['server_ports'])
            try:
                server = WebSocketServer("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server.start_server()
                status.update(label="runs", state="running", expanded=True)
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            st.session_state.client = True
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts1.markdown(st.session_state['client_ports'])
            try:
                uri = f'ws://localhost:{clientPort}'
                client = WebSocketClient(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client.startClient()
                st.session_state.client = client
                status.update(label="runs", state="running", expanded=True)
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

    if selectServ == "Bing":

        userInput1 = st.text_input("Ask agent_2")

        if startServer:            
            server_ports.append(websocketPort)
            st.session_state.server = True
            st.session_state['server_ports'] = server_ports
            serverPorts1.markdown(st.session_state['server_ports'])
            try:      
                server1 = WebSocketServer1("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server1.start_server()
                st.session_state.server = server1
                status.update(label="runs", state="running", expanded=True)
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            st.session_state.client = True
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts1.markdown(st.session_state['client_ports'])
            try:
                uri = f'ws://localhost:{clientPort}'
                client1 = WebSocketClient1(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client1.startClient()
                st.session_state.client = client1
                status.update(label="runs", state="running", expanded=True)
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")                

        if userInput1:
            user_input1 = st.chat_message("human")
            user_input1.markdown(userInput1)
            response = await handleUser2(userInput1)
            outputMsg1 = st.chat_message("ai") 
            outputMsg1.markdown(response)

    if selectServ == "GPT-3,5":
        
        userInput3 = st.text_input("Ask agent_2")

        if startServer:
            server_ports.append(websocketPort)
            st.session_state.server = True
            st.session_state['server_ports'] = server_ports
            serverPorts1.markdown(st.session_state['server_ports'])
            try:      
                server1 = WebSocketServer3("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server1.start_server()
                st.session_state.server = server1
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            st.session_state.client = True
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts1.markdown(st.session_state['client_ports'])
            try:
                uri = f'ws://localhost:{clientPort}'
                client1 = WebSocketClient3(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client1.startClient()
                st.session_state.client = client1
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")                

        if userInput3:
            user_input1 = st.chat_message("human")
            user_input1.markdown(userInput3)
            response = await handleUser3(userInput3)
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
            st.session_state.server = True
            st.session_state['server_ports'] = server_ports
            serverPorts1.markdown(st.session_state['server_ports'])
            st.session_state.tokenChar = token
            st.session_state.character_ID = characterID
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            st.session_state.user_ID = username
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
            st.session_state.client = True
            st.session_state['client_ports'] = client_ports
            clientPorts1.markdown(st.session_state['client_ports'])
            st.session_state.tokenChar = token
            st.session_state.character_ID = characterID
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            st.session_state.user_ID = username
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
            userID.markdown(st.session_state.user_ID)        
            try:            
                answer = await askCharacter(token, characterID, userInput2)
                outputMsg1 = st.chat_message("ai")
                outputMsg1.markdown(answer)

            except Exception as e:
                print(f"Error: {e}") 

    if selectServ == "Forefront":
        forefront_API = st.text_input("Fireworks API")        
        userInput = st.text_input("Ask agent 1")

        if startServer:
            st.session_state.forefront_api = forefront_API
            server_ports.append(websocketPort)
            st.session_state.server = True
            st.session_state['server_ports'] = server_ports
            serverPorts1.markdown(st.session_state['server_ports'])
            try:
                server = WebSocketServer4("localhost", websocketPort)    
                print(f"Starting WebSocket server on port {websocketPort}...")
                await server.start_server()
                status.update(label="runs", state="running", expanded=True)
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

        if runClient:
            st.session_state.client = True
            st.session_state.forefront_api = forefront_API
            client_ports.append(clientPort)
            st.session_state['client_ports'] = client_ports
            clientPorts1.markdown(st.session_state['client_ports'])
            try:
                uri = f'ws://localhost:{clientPort}'
                client = WebSocketClient4(uri)    
                print(f"Connecting client on port {clientPort}...")
                await client.startClient()
                st.session_state.client = client
                status.update(label="runs", state="running", expanded=True)
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")                

        if userInput:        
            print(f"User B: {userInput}")
            st.session_state.forefront_api = forefront_API
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            response3 = await handleUser4(userInput)
            print(response3)
            outputMsg = st.chat_message("ai") 
            outputMsg.markdown(response3) 

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
