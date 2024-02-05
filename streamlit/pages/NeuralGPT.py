import datetime
import websockets
import asyncio
import sqlite3
import json
import g4f
import streamlit as st
import fireworks.client
import streamlit.components.v1 as components
from PyCharacterAI import Client
from websockets.sync.client import connect

st.set_page_config(
    page_title='OCR Comparator', layout ="wide",
    initial_sidebar_state="expanded",
)

st.session_state.update(st.session_state)

servers = {}
clients = {}
inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()

client = Client()

system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

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

async def handleServer(ws):              
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
    print('New connection')
    await ws.send(instruction)
    while True:
        message = await ws.recv()        
        print(f'Received message: {message}')
        inputMsg = st.chat_message("assistant")
        inputMsg.markdown(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, message, timestamp))
        db.commit()   
        try:
            response = await chatCompletion(message)
            serverResponse = f"server: {response}"
            outputMsg = st.chat_message("ai") 
            print(serverResponse)
            outputMsg.markdown(response)
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()   
            # Append the server response to the server_responses list
            await ws.send(serverResponse)
            continue
                   
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

async def handleServer1(ws):              
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
    print('New connection')
    await ws.send(instruction)
    while True:
        message = await ws.recv()        
        print(f'Received message: {message}')
        inputMsg1 = st.chat_message("assistant")
        inputMsg1.markdown(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, message, timestamp))
        db.commit()   
        try:
            response = await askQuestion(message)
            serverResponse = f"server: {response}"
            outputMsg1 = st.chat_message("ai") 
            print(serverResponse)
            outputMsg1.markdown(response)
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, serverResponse, timestamp))
            db.commit()   
            # Append the server response to the server_responses list
            await ws.send(serverResponse)
            continue
                   
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

async def handleServer2(ws, chat): 
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. If you're unsure what you should do, ask the instance of higher hierarchy (server)" 
    print('New connection')
    await ws.send(instruction)    
    while True:
        message = await ws.recv()        
        print(f'Received message: {message}')
        inputMsg2 = st.chat_message("assistant")
        inputMsg2.markdown(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, message, timestamp))
        db.commit()   
        try:
            response = await chat.send_message(message)
            serverResponse = f"server: {response.text}"
            outputMsg2 = st.chat_message("ai") 
            print(serverResponse)
            outputMsg2.markdown(response.text)
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, response.text, timestamp))
            db.commit()   
            # Append the server response to the server_responses list
            await ws.send(response.text)
            continue
                   
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")   

async def askCharacter(token, characterID, question):    
    await client.authenticate_with_token(token)
    chat = await client.create_or_continue_chat(characterID)
    print(f"User B: {question}")
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
    db.commit()
    try:
        answer = await chat.send_message(question)
        print(f"{answer.src_character_name}: {answer.text}")
        timestamp = datetime.datetime.now().isoformat()
        serverSender = 'server'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, answer, timestamp))
        db.commit()
        return answer.text

    except Exception as e:
            print(f"Error: {e}")

# Start the WebSocket server 
async def start_websockets(fireworksAPI, websocketPort):
    global server
    fireworks.client.api_key = fireworksAPI
    async with websockets.serve(handleServer, 'localhost', websocketPort) as server:
        print(f"Starting WebSocket server on port {websocketPort}...")        
        servers[websocketPort] = server
        return server

async def start_websockets1(websocketPort):
    global server
    server = await websockets.serve(handleServer1, 'localhost', websocketPort)    
    print(f"Starting WebSocket server on port {websocketPort}...")        
    return server

async def start_websockets2(token, characterID, websocketPort):
    global server
    await client.authenticate_with_token(token)
    chat = await client.create_or_continue_chat(characterID)
    server = await websockets.serve(handleServer2, 'localhost', websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")        
    return chat, server

# Stop the WebSocket server
async def stop_websockets():    
    global server
    if server:
        # Close all connections gracefully
        server.close()
        # Wait for the server to close
        server.wait_closed()
        print("Stopping WebSocket server...")
    else:
        print("WebSocket server is not running.")

# Stop the WebSocket client
async def stop_client():
    global ws
    # Close the connection with the server
    ws.close()
    print("Stopping WebSocket client...")

async def main():

    st.session_state.update(st.session_state)

    if 'active_page' not in st.session_state:
        st.session_state.active_page = 'NeuralGPT'
    if "sidebar" not in st.session_state:
        st.session_state.sidebar = True
    if "server_ports" not in st.session_state:
        st.session_state['server_ports'] = False
    if "client_ports" not in st.session_state:
        st.session_state['client_ports'] = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = False
    if "servers" not in st.session_state:
        st.session_state.servers = None
    if "clients" not in st.session_state:
        st.session_state.clients = None    
    if "api_key" not in st.session_state:
        st.session_state.api_key = None          
    if "userID" not in st.session_state:
        st.session_state.userID = None

    st.text("Server ports:")
    serverPorts = st.sidebar.container(border=True)
    serverPorts.markdown(st.session_state['server_ports'])
    st.sidebar.text("Client ports")
    clientPorts = st.sidebar.container(border=True)
    clientPorts.markdown(st.session_state['client_ports'])
    st.sidebar.text("Charavter.ai ID")
    user_id = st.sidebar.container(border=True)
    user_id.markdown(st.session_state.userID)

    c1, c2 = st.columns(2)
    
    with c1:        
        serverPorts1 = st.container(border=True)
        serverPorts1.markdown(st.session_state['server_ports'])        
    
    with c2:
        clientPorts1 = st.container(border=True)
        clientPorts1.markdown(st.session_state['client_ports'])        
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Fireworks", "GPT4Free", "Character.ai", "Chaindesk agent", "Docsbot Wordpress-agent", "Flowise client"])

    with tab1:        
        st.header("Fireworks Llama2-7B")
        fireworksAPI = st.text_input("Fireworks API key")
        row1_col1, row1_col2 = st.columns(2)
        userInputt = st.text_input("User input")
        
        with row1_col1:
            websocket_Port = st.number_input("Server port", 1000)
            startServer = st.button('Start websocket server 1')
            srvr_ports = st.container(border=True)
            srvr_ports.markdown(st.session_state['server_ports'])
        
        with row1_col2:            
            client_Port = st.number_input("Client port", 1000)
            startClient = st.button('Connect client to server 1')
            cli_ports = st.container(border=True)
            cli_ports.markdown(st.session_state['client_ports'])

        if userInputt:        
            print(f"User B: {userInputt}")
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            user_input = st.chat_message("human")
            user_input.markdown(userInputt)
            response1 = await handleUser(userInputt)
            print(response1)
            outputMsg = st.chat_message("ai") 
            outputMsg.markdown(response1)

        if startServer:
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key            
            st.session_state['server_ports'] = server_ports.append(websocket_Port)
            serverPorts.markdown(st.session_state['server_ports'])
            serverPorts1.markdown(st.session_state['server_ports'])
            srvr_ports.markdown(st.session_state['server_ports'])
            try:
                server = await websockets.serve(handleServer, 'localhost', websocket_Port)
                st.session_state.servers = servers[server]
                print(f"Launching server at port: {websocket_Port}")
                while True:
                    await server.wait_closed()
            except Exception as e:
                print(f"Error: {e}") 


        if startClient:
            fireworks.client.api_key = fireworksAPI
            st.session_state.api_key = fireworks.client.api_key
            st.session_state['client_ports'] = client_ports.append(client_Port)
            clientPorts.markdown(st.session_state['client_ports'])
            clientPorts1.markdown(st.session_state['client_ports'])
            cli_ports.markdown(st.session_state['client_ports'])
            print(f"Connecting to server at port: {client_Port}...")          
            uri = f'ws://localhost:{client_Port}'
            async with websockets.connect(uri) as websocket:
                while True:                    
                    # Listen for messages from the server
                    input_message = await websocket.recv()
                    print(f"Server: {input_message}")
                    input_Msg = st.chat_message("assistant")
                    input_Msg.markdown(input_message)
                    try:
                        response = await chatCompletion(input_message)
                        res1 = f"Client: {response}"
                        output_Msg = st.chat_message("ai")
                        output_Msg.markdown(res1)
                        await websocket.send(json.dumps(res1))

                    except websockets.ConnectionClosed:
                        print("client disconnected")
                        continue

                    except Exception as e:
                        print(f"Error: {e}")
                        continue

    with tab2:
        st.header("GPT4Free Client")
        userInput1 = st.text_input("User input 1")
        col1, col2 = st.columns(2)

        with col1:
            websocketPort1 = st.number_input("G4F Server port", 1000)
            startServer1 = st.button('Start websocket server 2')
            srvr_ports1 = st.container(border=True)
            srvr_ports1.text("Websocket server ports")

        with col2:
            clientPort1 = st.number_input("G4F Client port", 1000)
            startClient1 = st.button('Connect client to server 2')
            cli_ports1 = st.container(border=True)
            cli_ports1.text("Websocket client ports")
        
        if userInput1:
            user_input1 = st.chat_message("human")
            user_input1.markdown(userInput1)
            response = await handleUser2(userInput1)
            outputMsg1 = st.chat_message("ai") 
            outputMsg1.markdown(response)

        if startServer1:
            server_ports.append(websocketPort1)
            serverPorts.markdown(server_ports)
            serverPorts1.markdown(server_ports)
            srvr_ports1.markdown(server_ports)
            try:
                server1 = await websockets.serve(handleServer1, 'localhost', websocketPort1)
                print(f"Launching server at port: {websocketPort1}")
                while True:
                    await server1.wait_closed()

            except Exception as e:
                print(f"Error: {e}") 
                    

        if startClient1:
            client_ports.append(clientPort1)
            clientPorts.markdown(client_ports)
            clientPorts1.markdown(client_ports)
            cli_ports1.markdown(client_ports)
            uri1 = f'ws://localhost:{clientPort1}'
            async with websockets.connect(uri1) as websocket:
                while True:
                    print(f"Connecting to server at port: {clientPort1}...")
                    # Listen for messages from the server
                    input_message1 = await websocket.recv()
                    print(f"Server: {input_message1}")
                    input_Msg1 = st.chat_message("assistant")
                    input_Msg1.markdown(input_message1)
                    try:
                        response1 = await askQuestion(input_message1)
                        res = f"Client: {response1}"
                        print(res)
                        output_Msg1 = st.chat_message("ai")
                        output_Msg1.markdown(res)
                        await websocket.send(json.dumps(res))

                    except websockets.ConnectionClosed:
                        print("client disconnected")
                        continue               

                    except Exception as e:
                        print(f"Error: {e}") 
                        continue

    with tab3:
        st.header("Character AI Client")
        token = st.text_input("Character AI Token")
        userID = st.container(border=True)
        characterID = st.text_input("Character ID")
        co1, co2 = st.columns(2)
        userInput2 = st.text_input("User input 2")

        with co1:
            websocketPort2 = st.number_input("Character AI Server port", 1000)
            startServer2 = st.button('Start websocket server 3')
            srvr_ports2 = st.container(border=True)

        with co2:
            clientPort2 = st.number_input("Character AI Client port", 1000)
            startClient2 = st.button('Connect client to server 3')
            cli_ports2 = st.container(border=True)
            cli_ports2.text("Websocket client ports")

        if startServer2:
            server_ports.append(websocketPort2)
            serverPorts.markdown(server_ports)
            serverPorts1.markdown(server_ports)
            srvr_ports2.markdown(server_ports)
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            user_id.markdown(username)
            userID.markdown(username)
            try:
                server2 = await websockets.serve(handleServer2, 'localhost', websocketPort2)
                print(f"Launching server at port: {websocketPort2}")
                while True:
                    await server2.wait_closed()

            except Exception as e:
                print(f"Error: {e}") 


        if startClient2:
            client_ports.append(clientPort2)
            clientPorts.markdown(client_ports)
            clientPorts1.markdown(client_ports)
            cli_ports2.markdown(client_ports)
            uri2 = f'ws://localhost:{clientPort2}'
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            user_id.markdown(username)
            userID.markdown(username)
            chat = await client.create_or_continue_chat(characterID)
            print(f"Connecting to server at port: {clientPort2}...")
            async with websockets.connect(uri2) as websocket:
                while True:                    
                    # Listen for messages from the server
                    input_message2 = await websocket.recv()
                    print(f"Server: {input_message2}")
                    input_Msg2 = st.chat_message("assistant")
                    input_Msg2.markdown(input_message2)                    
                    try:
                        response2 = await chat.send_message(input_message2)
                        print(f"Client: {response2.text}")
                        output_Msg2 = st.chat_message("ai")
                        output_Msg2.markdown(response2.text)
                        await websocket.send(json.dumps(response2.text))

                    except websockets.ConnectionClosed:
                        print("client disconnected")
                        continue               

                    except Exception as e:
                        print(f"Error: {e}")
                        continue

        if userInput2:
            user_input2 = st.chat_message("human")
            user_input2.markdown(userInput2)
            await client.authenticate_with_token(token)
            username = (await client.fetch_user())['user']['username']
            user_id.markdown(username)
            userID.markdown(username)
            try:
                chat = await client.create_or_continue_chat(characterID)
                answer = await chat.send_message(userInput2)
                print(f"{answer.src_character_name}: {answer.text}")
                outputMsg2 = st.chat_message("ai")
                outputMsg2.markdown(answer.text)

            except Exception as e:
                print(f"Error: {e}") 

    with tab4:
        HtmlFile = open("comp.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code)

    with tab5:
        HtmlFile = open("Docsbotport.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code)

    with tab6:
        HtmlFile = open("flowise.html", 'r', encoding='utf-8')
        source_code = HtmlFile.read() 
        components.html(source_code)

asyncio.run(main())