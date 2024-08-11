import os
import sqlite3
import websockets
import json
import asyncio
import time
import streamlit as st
from io import StringIO
from agents import Llama2, Copilot, ChatGPT, Claude3, ForefrontAI, Flowise, Chaindesk, CharacterAI
import conteneiro

st.set_page_config(layout="wide")

servers = []
clients = []
inputs = []
outputs = []
used_ports = []
credentials = []
server_ports = []
client_ports = []

async def main():

    if "googleAPI" not in st.session_state:
        st.session_state.googleAPI = ""        
    if "cseID" not in st.session_state:
        st.session_state.cseID = ""                        
    if "api_key" not in st.session_state:
        st.session_state.api_key = "" 
    if "fireworks_api" not in st.session_state:
        st.session_state.fireworks_api = ""
    if "anthropicAPI" not in st.session_state:
        st.session_state.anthropicAPI = ""
    if "server_ports" not in st.session_state:
        st.session_state['server_ports'] = ""
    if "client_ports" not in st.session_state:
        st.session_state['client_ports'] = ""
    if "servers" not in st.session_state:
        st.session_state['servers'] = ""
    if "clients" not in st.session_state:
        st.session_state['clients'] = ""
    if "gradio_Port" not in st.session_state:
        st.session_state.gradio_Port = "" 
    if "server" not in st.session_state:
        st.session_state.server = False    
    if "client" not in st.session_state:
        st.session_state.client = False
    if "user_ID" not in st.session_state:
        st.session_state.user_ID = ""
    if "forefront_api" not in st.session_state:
        st.session_state.forefront_api = ""
    if "tokenChar" not in st.session_state:
        st.session_state.tokenChar = ""
    if "charName" not in st.session_state:
        st.session_state.charName = ""
    if "character_ID" not in st.session_state:
        st.session_state.character_ID = ""
    if "flow" not in st.session_state:
        st.session_state.flow = ""
    if "agentID" not in st.session_state:
        st.session_state.agentID = ""
    if "tokens" not in st.session_state:
        st.session_state.tokens = None
    if 'credentials' not in st.session_state:
        st.session_state.credentials = []
    if "server_state" not in st.session_state:
        st.session_state.server_state = "complete"
    if "client_state" not in st.session_state:
        st.session_state.client_state = "complete"    
     
    APItokens = {
        "APIfireworks": str(st.session_state.fireworks_api),
        "APIforefront": str(st.session_state.forefront_api),
        "APIanthropic": str(st.session_state.anthropicAPI),
        "TokenCharacter": str(st.session_state.tokenChar),
        "char_ID": str(st.session_state.character_ID),
        "chaindeskID": str(st.session_state.agentID),
        "FlowiseID": str(st.session_state.flow)
    }

    json_credentials = json.dumps(APItokens)
    print(json_credentials)

    with st.expander("Personal API tokens"):
        uploadAPI = st.file_uploader(label="Upload credentials")
        fire = st.empty()        
        fore = st.empty()        
        anthro = st.empty()
        char = st.empty()        
        charID = st.empty()        
        chain = st.empty()        
        flo = st.empty()
        saveAPI = st.download_button(label="Download API tokens",
                        data=json_credentials,
                        file_name=f"APItokens.json",
                        mime="application/json",
                        help="Click to save your API keys")

        if st.session_state.tokens == None:
            fireworks_api = fire.text_input("Fireworks API")
            forefront_api = fore.text_input("Forefront AI API")
            anthropic_api = anthro.text_input("Anthropic API")
            characterToken = char.text_input("Character.ai personal token")
            character_ID = charID.text_input("Character ID")
            chaindeskAgent = chain.text_input("Chaindesk agent ID")
            flowID = flo.text_input("Flowise flow ID")

    c1, c2 = st.columns(2)

    selectAgent = st.selectbox("Select agent", ("Llama 3", "Copilot", "ChatGPT", "Forefront AI", "Claude-3", "Character.ai", "Chaindesk", "Flowise"))
    sys_instruction = st.checkbox("System instruction")
    userInput = st.chat_input("Ask Agent")

    with c1:
        websocketPort = st.number_input("Websocket server port", min_value=1000, max_value=9999, value=1000)   
        startServer = st.button("Start server")
        stopServer = st.button("Stop server")
        st.text("Servers")
        serverPorts1 = st.empty()
        serverPorts = serverPorts1.status(label="websocket servers", state="complete", expanded=False)
        serverPorts.write(conteneiro.servers)
    
    with c2:
        clientPort = st.number_input("Websocket client port", min_value=1000, max_value=9999, value=1000)
        runClient = st.button("Start client")
        stopClient = st.button("Stop client")        
        st.text("Websocket clients")
        clientPorts1 = st.empty()
        clientPorts = clientPorts1.status(label="websocket clients", state="complete", expanded=False)
        clientPorts.write(conteneiro.clients)

    with st.sidebar:
        # Wyświetlanie danych, które mogą być modyfikowane na różnych stronach       
        st.text("Websocket servers")
        srv_status = st.empty()
        server_status1 = srv_status.status(label="websocket servers", state="complete", expanded=True)
        server_status1.write(conteneiro.servers)
        if st.session_state.server == True:
            st.session_state.server_state = "running"
            srv_status.empty()
            server_status1 = srv_status.status(label="websocket servers", state=st.session_state.server_state, expanded=True)
            server_status1.write(conteneiro.servers)

        st.text("Websocket clients")
        cli_status = st.empty()
        client_status1 = cli_status.status(label="websocket clients", state="complete", expanded=True)
        client_status1.write(conteneiro.clients)
        if st.session_state.client == True:
            st.session_state.client_state = "running"
            cli_status.empty()
            client_status1 = cli_status.status(label="websocket clients", state=st.session_state.client_state, expanded=True)
            client_status1.write(conteneiro.clients)

    if uploadAPI is not None:

        data = json.load(uploadAPI)
        print(data)

        st.session_state.fireworks_api = data["APIfireworks"]
        
        if st.session_state.fireworks_api == "":
            fireworks_api = fire.text_input("Fireworks API key")
        else:
            fireworks_api = fire.container(border=True)
            fireworks_api.write(str(st.session_state.fireworks_api))

        st.session_state.forefront_api = data["APIforefront"]
        
        if  st.session_state.forefront_api == "":
            forefront_api = fore.text_input("Forefront API key")
        else:
            forefront_api = fore.container(border=True)
            forefront_api.write(str(st.session_state.forefront_api))

        st.session_state.anthropicAPI = data["APIanthropic"]

        if st.session_state.anthropicAPI == "":
            anthropic_api = anthro.text_input("Anthropic API key")
        else:
            anthropic_api = anthro.container(border=True)
            anthropic_api.write(str(st.session_state.anthropicAPI))

        st.session_state.tokenChar = data["TokenCharacter"]

        if st.session_state.tokenChar == "":
            characterToken = char.text_input("Character.ai user token")
        else:
            characterToken = char.container(border=True)
            characterToken.write(str(st.session_state.tokenChar))

        st.session_state.character_ID = data["char_ID"]

        if st.session_state.character_ID == "":
            character_ID = charID.text_input("Your Character ID")
        else:
            character_ID = charID.container(border=True)
            character_ID.write(str(st.session_state.character_ID))

        st.session_state.agentID = data["chaindeskID"]

        if st.session_state.agentID == "":
            chaindeskAgent = chain.text_input("Chaindesk agent ID:")
        else:
            chaindeskAgent = chain.container(border=True)
            chaindeskAgent.write(str(st.session_state.agentID))

        st.session_state.flow = data["FlowiseID"]

        if st.session_state.flow == "":
            flowID = flo.text_input("Flowise flow ID:")
        else:
            flowID = flo.container(border=True)
            flowID.write(str(st.session_state.flow))

    if saveAPI:
        credentials.clear()
        st.session_state.fireworks_api = fireworks_api
        credentials.append(st.session_state.fireworks_api)
        st.session_state.forefront_api = forefront_api
        credentials.append(st.session_state.forefront_api)
        st.session_state.anthropicAPI = anthropic_api
        credentials.append(st.session_state.anthropicAPI)
        st.session_state.tokenChar = characterToken
        credentials.append(st.session_state.tokenChar)
        st.session_state.character_ID = character_ID
        credentials.append(st.session_state.character_ID)
        st.session_state.agentID = chaindeskAgent
        credentials.append(st.session_state.agentID)
        st.session_state.flow = flowID
        credentials.append(st.session_state.flow)

    if  sys_instruction:
        sys_prompt = st.text_input("System instruction")

    else:
        sys_prompt = f"You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. As instance of higher hierarchy in the NeuralGPT framework, your response will have an automatic follow-up in which you will be able to take additional actions if they are required from you."

    if  selectAgent == "Llama 3":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = Llama2(str(st.session_state.fireworks_api))
            results = await agent.handleUser(sys_prompt, userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name = f"Llama 3 client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = Llama2(str(st.session_state.fireworks_api))             
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name = f"Llama2 server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = Llama2(str(st.session_state.fireworks_api))              
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "Copilot":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = Copilot()
            results = await agent.handleUser(sys_prompt, userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name1 = f"Copilot client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name1, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name1, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = Copilot()
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name1 = f"Copilot server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label="websocket servers", state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label="websocket servers", state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = Copilot()
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "ChatGPT":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = ChatGPT()
            results = await agent.handleInput(userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name2 = f"GPT-3,5 client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name2, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name2, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = ChatGPT()         
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name2 = f"GPT-3,5 server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name2, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name2, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = ChatGPT()
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "Forefront AI":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = ForefrontAI(str(st.session_state.forefront_api))
            results = await agent.handleUser(sys_prompt, userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name = f"Forefront AI client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = ForefrontAI(str(st.session_state.forefront_api))        
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name = f"Forefroont AI server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = ForefrontAI(str(st.session_state.forefront_api))
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "Claude-3":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = Claude3(str(st.session_state.anthropicAPI))
            results = await agent.handleUser(sys_prompt, userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name = f"Claude-3 client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = Claude3(str(st.session_state.anthropicAPI))
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name = f"Claude-3 server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = Claude3(str(st.session_state.anthropicAPI))        
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "Character.ai":

        usrToken = str(st.session_state.tokenChar)
        charID = str(st.session_state.character_ID)

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = CharacterAI(usrToken, charID)
            results = await agent.handleInput(userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name = f"Claude-3 client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = CharacterAI(usrToken, charID)
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name = f"Claude-3 server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = CharacterAI(usrToken, charID)
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "Chaindesk":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = Chaindesk(str(st.session_state.agentID))   
            results = await agent.handleInput(userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name = f"Claude-3 client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = Chaindesk(str(st.session_state.agentID))
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name = f"Claude-3 server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = Chaindesk(str(st.session_state.agentID))
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

    if  selectAgent == "Flowise":

        if userInput:
            print(f"User B: {userInput}")
            user_input = st.chat_message("human")
            user_input.markdown(userInput)
            agent = Flowise(str(st.session_state.flow))
            results = await agent.handleInput(userInput)
            print(results)

        if runClient:
            st.session_state.client = True
            cli_name = f"Claude-3 client port: {clientPort}"
            cli_status.empty()
            client_status1 = cli_status.status(label=cli_name, state="running", expanded=True)
            client_status1.write(conteneiro.clients)
            clientPorts1.empty()            
            clientPorts = clientPorts1.status(label=cli_name, state="running", expanded=True)
            clientPorts.write(conteneiro.clients)            
            try:
                client = Flowise(str(st.session_state.flow))
                await client.startClient(clientPort)
                print(f"Connecting client on port {clientPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")              

        if startServer:
            st.session_state.server = True
            srv_name = f"Claude-3 server port: {websocketPort}"
            srv_status.empty()
            server_status1 = srv_status.status(label=srv_name, state="running", expanded=True)
            server_status1.write(conteneiro.servers)
            serverPorts1.empty()
            serverPorts = serverPorts1.status(label=srv_name, state="running", expanded=True)
            serverPorts.write(conteneiro.servers)            
            try:
                server = Flowise(str(st.session_state.flow))
                await server.start_server(websocketPort)
                print(f"Starting WebSocket server on port {websocketPort}...")
                await asyncio.Future()

            except Exception as e:
                print(f"Error: {e}")

asyncio.run(main())