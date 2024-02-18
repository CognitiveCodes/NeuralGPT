import streamlit as st
import datetime
import asyncio
import sqlite3
import g4f
import websockets
import streamlit as st
import fireworks.client
import gradio as gr
import streamlit.components.v1 as components
from PyCharacterAI import Client
from ServG4F import WebSocketServer1
from ServFire import WebSocketServer
from ServChar import WebSocketServer2
from clientG4F import WebSocketClient1
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
chat_history = []
ports_g4f = []
ports_fire = []
serv_char = []
serv_g4f = []

system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()

st.set_page_config(layout="wide")

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

async def chatCompletion(fireworksAPI, question):
    fireworks.client.api_key = fireworksAPI
    st.session_state.api_key = fireworksAPI
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

async def main():

    if "server_ports" not in st.session_state:
        st.session_state['server_ports'] = ""
    if "client_ports" not in st.session_state:
        st.session_state['client_ports'] = ""
    if "chat_history" not in st.session_state:
        st.session_state['chat_history'] = ""
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

    gradioPorts = st.container(border=True)
    gradioPort = st.number_input("Gradio server port", min_value=1000, max_value=9999, value=1000)
    startGradio = st.button("Start Gradio")

    st.sidebar.text("Server ports:")
    serverPorts = st.sidebar.container(border=True)
    serverPorts.markdown(st.session_state['server_ports'])
    st.sidebar.text("Client ports")
    clientPorts = st.sidebar.container(border=True)
    clientPorts.markdown(st.session_state['client_ports'])
    st.sidebar.text("Character.ai ID")
    user_id = st.sidebar.container(border=True)
    user_id.markdown(st.session_state.user_ID)
    chat_Area = st.container(border=True)    


    
    async def askCharacter(token, character_ID, question):

        chatbox2 = st.container(border=True)

        await client.authenticate_with_token(token)
        username = (await client.fetch_user())['user']['username']
        chat = await client.create_or_continue_chat(character_ID)
        input = f"User B: {question}"
        chatbox2.chat_message("human").write(input)
        st.session_state.tokenChar = token
        st.session_state.charName = username
        st.session_state.character_ID = character_ID
        st.session_state.user_ID = username
        
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, question, timestamp))
        db.commit()
        try:
            answer = await chat.send_message(input)
            response = f"{answer.src_character_name}: {answer.text}"
            print(response)
            chatbox2.chat_message("ai").write(response)
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, response, timestamp))
            db.commit()
            return response

        except Exception as e:
                print(f"Error: {e}")    

        with st.sidebar:
            user_id = st.sidebar.container(border=True)
            user_id.markdown(st.session_state.user_ID)

    async def handleUser(fireworksAPI, userInput): 
        
        question = f"User B: {userInput}"
        print(question)
        chat_Area.markdown(question)            
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, question, timestamp))
        db.commit()
        try:
            response2 = await chatCompletion(fireworksAPI, question)
            response = f"Llama2: {response2}"
            chat_Area.markdown(response)

            serverSender = 'server'
            timestamp = datetime.datetime.now().isoformat()
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, response, timestamp))
            db.commit()
            return response

        except Exception as e:
            print(f"Error: {e}")

    async def handleUser2(userInput):
        
        question = f"User B: {userInput}"
        print(question)
        user_input = st.chat_message("human")
        chat_history.append(question)
        user_input.markdown(question)            
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, question, timestamp))
        db.commit()
        try:
            response3 = await askQuestion(question)
            response = f"GPT4Free: {response3}"
            chat_Area.markdown(response)
            serverSender = 'server'
            timestamp = datetime.datetime.now().isoformat()
            db = sqlite3.connect('chat-hub.db')
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                        (serverSender, response3, timestamp))
            db.commit()
            return response3

        except Exception as e:
            print(f"Error: {e}")

    # Start the WebSocket server 
    async def run_websockets(fireworks_API, websocketPort):
        global server
        fireworks.client.api_key = fireworks_API
        st.session_state.api_key = fireworks_API
        server_ports.append(websocketPort)
        try:
            server = WebSocketServer("localhost", websocketPort)    
            print(f"Starting WebSocket server on port {websocketPort}...")
            await server.start_server()
            serverPorts.markdown(server_ports)
            return "Used ports:\n" + '\n'.join(map(str, server_ports))

        except Exception as e:
            print(f"Error: {e}")

    # Start the WebSocket server1 
    async def run_websockets1(websocketPort):
        global server
        serv_g4f.append(websocketPort)            
        try:
            server = WebSocketServer1("localhost", websocketPort)    
            print(f"Starting WebSocket server on port {websocketPort}...")
            await server.start_server()
            return "Used ports:\n" + '\n'.join(map(str, server_ports))

        except Exception as e:
                    print(f"Error: {e}")

        with st.sidebar:
            portsG4F = st.container(border=True)
            portsG4F.markdown(serv_g4f)                 

    async def run_websockets2(websocketPort, token, characterID):
        global server
        client = Client()
        serv_char.append(websocketPort)
        await client.authenticate_with_token(token)
        username = (await client.fetch_user())['user']['username']        
        user_id.markdown(username)
        st.session_state.user_ID = username
        st.session_state.character_ID = characterID
        st.session_state.tokenChar = token
        try:      
            server2 = WebSocketServer2("localhost", websocketPort)    
            print(f"Starting WebSocket server on port {websocketPort}...")
            await server.start_server()
            return "Used ports:\n" + '\n'.join(map(str, server_ports))

        except Exception as e:
            print(f"Error: {e}")

        with st.sidebar:
            char_ports = st.sidebar.container(border=True)
            char_ports.markdown(serv_char)

    async def run_client(fireworksAPI, clientPort):
        
        chat_Area = st.container(border=True)

        with st.sidebar:        
            fire_ports = st.container(border=True)
            fire_ports.markdown(ports_fire)     

        uri = f'ws://localhost:{clientPort}'
        ports_fire.append(clientPort)
        
        async with websockets.connect(uri) as ws:        
            while True:                
                # Listen for messages from the server            
                input_message = await ws.recv()
                question = f"server: {input_message}"
                chat_Area.markdown(question)
                
                output_message = await chatCompletion(fireworksAPI, input_message)
                response = f"client: {output_message}"
                chat_Area.markdown(response)

                await ws.send(output_message)
                await asyncio.sleep(0.1)

                
    async def run_client1(clientPort):

        g4f_ports = st.sidebar.container(border=True)
        g4f_ports.markdown("GPT4Free clients: ")

        chatbox1 = st.container(border=True)

        uri = f'ws://localhost:{clientPort}'
        ports_g4f.append(clientPort)
        g4f_ports.markdown(ports_g4f)
        async with websockets.connect(uri) as ws:
            while True:                
                # Listen for messages from the server            
                input_message = await ws.recv()
                input_msg = f"server: {input_message}"
                chatbox1.markdown(input_msg)
                
                output_message = await askQuestion(input_msg)
                response = f"client: {output_message}"
                chatbox1.markdown(response)             

                await ws.send(response)
                await asyncio.sleep(0.1)           

    async def run_character(characterPort, token, characterID):    

        clientPorts = st.sidebar.container(border=True)

        uri = f'ws://localhost:{characterPort}'
        client_ports.append(characterPort)
        clientPorts.markdown(client_ports)
        st.session_state.tokenChar = token
        st.session_state.character_ID = characterID
        await client.authenticate_with_token(token)
        username = (await client.fetch_user())['user']['username']
        st.session_state.charName = username    
        async with websockets.connect(uri) as ws:        
            while True:
                # Listen for messages from the server            
                question = await ws.recv()
                input_msg = f"server: {question}"
                chat_Area.markdown(input_msg)

                chat = await client.create_or_continue_chat(characterID)
                answer = await chat.send_message(question)
                response = f"{answer.src_character_name}: {answer.text}"
                chat_Area.markdown(response)            

                print(f"{answer.src_character_name}: {answer.text}")
                await ws.send(answer.text)        

    async def connector(token):
        await client.authenticate_with_token(token)    
        username = (await client.fetch_user())['user']['username']
        print(f'Authenticated as {username}')
        return username
        
    async def askCharacter(token, character_id, question):

        chat_Area = st.container(border=True)
    
        await client.authenticate_with_token(token)        
        userInput = f"User B: {question}" 
        chat_Area.markdown(userInput)
        username = (await client.fetch_user())['user']['username']
        st.session_state.user_ID = username
        st.sidebar.markdown(username)
        chat = await client.create_or_continue_chat(character_id)
        answer = await chat.send_message(question)
        response = f"{answer.src_character_name}: {answer.text}"
        chat_Area.markdown(response)
        print(f"{answer.src_character_name}: {answer.text}")
        return response

    # Stop the WebSocket server
    async def stop_websockets():    
        global server
        if server:
            # Close all connections gracefully
            server.close()
            # Wait for the server to close
            await server.wait_closed()
            print("Stopping WebSocket server...")
        else:
            print("WebSocket server is not running.")

    st.session_state.gradio_Port = gradioPort
    gradioPorts.markdown(st.session_state.gradio_Port)        
    openPage = st.toggle('View Gradio app')
    link = f"http://127.0.0.1:{gradioPort}"
    st.link_button("Open Gradio in new tab", link)

    if openPage:
        txt = st.text_input("sokolwiekto")
        chatbox1 = st.container(border=True)
        url = f"http://127.0.0.1:{st.session_state.gradio_Port}"
        st.components.v1.iframe(url, height=950, scrolling=True)     

    if startGradio:

        chatbox = st.container(border=True)
        chatbox.markdown("chuj")

        with gr.Blocks() as demo:
            with gr.Tabs(elem_classes="tab-buttons") as tabs:
                with gr.TabItem("Fireworks Llama2", elem_id="fireworks_server", id=0):
                    with gr.Row():
                        # Use the client_messages list to update the messageTextbox
                        client_msg = gr.Textbox(lines=5, max_lines=130, label="Client messages", interactive=False)     
                        # Use the server_responses list to update the serverMessageTextbox
                        server_msg = gr.Textbox(lines=5, max_lines=130, label="Server responses", interactive=False)                       
                    with gr.Row():
                        chudee = st.container(border=True)
                        user_Input = gr.Textbox(label="User Input")
                    with gr.Row():    
                        ask_Qestion = gr.Button("Ask chat/conversational node")
                        chuj = st.container(border=True)
                    with gr.Row():
                        fireworks_API = gr.Textbox(label="Fireworks API key")
                    with gr.Row():    
                        websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                        port = gr.Textbox()                  
                    with gr.Row():    
                        startServer = gr.Button("Start WebSocket Server")            
                        stopWebsockets = gr.Button("Stop WebSocket Server")
                    with gr.Row():
                        clientPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                        startClient = gr.Button("Start WebSocket client")
                        stopClient = gr.Button("Stop WebSocket client")
                    with gr.Row():
                        PortInUse = gr.Textbox()    
                
                with gr.TabItem("GPT4Free Client", elem_id="gpt4free", id=2):
                    with gr.Row():
                        # Use the client_messages list to update the messageTextbox
                        client_msg1 = gr.Textbox(lines=5, max_lines=130, label="Client messages", interactive=False)     
                        # Use the server_responses list to update the serverMessageTextbox
                        server_msg1 = gr.Textbox(lines=5, max_lines=130, label="Server responses", interactive=False)                       
                    with gr.Row():
                        userInput1 = gr.Textbox(label="User Input")
                    with gr.Row():    
                        askG4F = gr.Button("Ask chat/conversational node")
                    with gr.Row():
                        websocketPort1 = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                        port1 = gr.Textbox()                        
                    with gr.Row():   
                        startServer1 = gr.Button("Start WebSocket Server")
                        stopWebsockets1 = gr.Button("Stop WebSocket Server")
                    with gr.Row():
                        clientPort1 = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                        startClient1 = gr.Button("Start WebSocket client")
                        stopClient1 = gr.Button("Stop WebSocket client")
                    with gr.Row():
                        PortInUse1 = gr.Textbox()

                with gr.TabItem("CharacterAI Client", elem_id="characterai_client", id=1):
                    with gr.Row():
                        # Use the client_messages list to update the messageTextbox
                        clientMsg = gr.Textbox(lines=5, max_lines=130, label="Client messages", interactive=False)
                        # Use the  gr.Textbox(label="User Input")
                        serverMsg = gr.Textbox(lines=5, max_lines=130, label="Server responses", interactive=False) 
                    with gr.Row():
                        userInput2 = gr.Textbox(label="User Input")                    
                    with gr.Row():                        
                        ask_question = gr.Button("Ask Character")
                    with gr.Row():
                        token = gr.Textbox(label="User Token")
                        character_id = gr.Textbox(label="Character ID")
                    with gr.Row():
                        connect = gr.Button("Connect to Character.ai")                        
                        user = gr.Textbox(label="User ID")
                    with gr.Row():
                        websocketsPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                        ports = gr.Textbox()
                    with gr.Row(): 
                        start_Server = gr.Button("Start WebSocket Server")            
                        stop_Websockets = gr.Button("Stop WebSocket Server")
                    with gr.Row():
                        characterPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
                        Client_Ports = gr.Textbox()
                    with gr.Row():
                        startCharacter = gr.Button("Start WebSocket client")
                        stop_Client = gr.Button("Stop WebSocket client")

                        startServer.click(run_websockets, inputs=[fireworks_API, websocketPort], outputs=port)
                        startClient.click(run_client, inputs=[fireworks_API, clientPort], outputs=None)
                        stopWebsockets.click(stop_websockets, inputs=None, outputs=port)
                        ask_Qestion.click(handleUser, inputs=[fireworks_API, user_Input], outputs=client_msg)
                        
                        askG4F.click(handleUser2, inputs=userInput1, outputs=server_msg1)
                        startServer1.click(run_websockets1, inputs=websocketPort1, outputs=port1)
                        startClient1.click(run_client1, inputs=clientPort1, outputs=None)
                        stop_Websockets.click(stop_websockets, inputs=None, outputs=port1)

                        start_Server.click(run_websockets2, inputs=[token, character_id, websocketsPort], outputs=ports)
                        startCharacter.click(run_character, inputs=[characterPort, token, character_id], outputs=None)
                        stop_Websockets.click(stop_websockets, inputs=None, outputs=ports)
                        connect.click(connector, inputs=token, outputs=user)
                        ask_question.click(askCharacter, inputs=[token, character_id, userInput2], outputs=serverMsg)
        
        gr_port = int(gradioPort)
        st.session_state.gradio_Port = gr_port        
        demo.queue()    
        demo.launch(share=True, server_port=gr_port)
        gradioPorts.markdown(st.session_state.gradio_Port)

asyncio.run(main())
