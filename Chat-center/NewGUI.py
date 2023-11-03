import datetime
import os
import sqlite3
import websockets
import websocket
import asyncio
import sqlite3
import json
import requests
import asyncio
import time
import gradio as gr
import fireworks.client
import PySimpleGUI as sg
from websockets.sync.client import connect
from tempfile import TemporaryDirectory
from langchain.load.dump import dumps
from langchain import hub
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage
from langchain.agents.agent_toolkits import FileManagementToolkit
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.fireworks import Fireworks
from langchain.chat_models.fireworks import ChatFireworks
from langchain.tools.render import render_text_description
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.output_parsers import PydanticOutputParser, CommaSeparatedListOutputParser

from langchain.output_parsers.json import SimpleJsonOutputParser

from langchain.callbacks.streaming_stdout_final_only import (
    FinalStreamingStdOutCallbackHandler,
)
from langchain.prompts.chat import (
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.tools.file_management import (
    ReadFileTool,
    CopyFileTool,
    DeleteFileTool,
    MoveFileTool,
    WriteFileTool,
    ListDirectoryTool,
)
from langchain.agents import (
    Tool,
    ZeroShotAgent,
    BaseMultiActionAgent,
    create_sql_agent,
    load_tools,
    initialize_agent,
    AgentType,
    AgentExecutor,
)

# Define the global constants for the API keys
GOOGLE_CSE_ID = "cse id"
GOOGLE_API_KEY = "google api"
FIREWORKS_API_KEY = "Fireworks api"

fireworks.client.api_key = "another Fireworks api"
            
os.chdir("E:/repos/chat-hub/virtual/NeuralGPT")
working_directory = "E:/repos/chat-hub/virtual/NeuralGPT"

class BaseCallbackHandler:
    """Base callback handler that can be used to handle callbacks from langchain."""

inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

layout = [
    [sg.Multiline(size=(200, 10), key='-CLIENT-')],
    [sg.Multiline(size=(102, 20), key='-INPUT-', auto_refresh=True), sg.Multiline(size=(102, 20), key='-OUTPUT-', auto_refresh=True)],
    [sg.Multiline(size=(150, 2), key='-USERINPUT-'),
     sg.Button('Ask the agent')],
    [sg.InputText(size=(10, 1), key='-PORT-'), sg.Slider(range=(1000, 9999), orientation='h', size=(20, 20), key='-PORTSLIDER-'),
     sg.Text('Server Port:')],
     [sg.InputText(size=(10, 1), key='-PORT1-'), sg.Slider(range=(1000, 9999), orientation='h', size=(20, 20), key='-PORTSLIDER1-'),
      sg.Text('Client Port:')],
    [sg.Button('Start WebSocket server'), sg.Button('Start WebSocket client')],
    [sg.Button('Stop WebSocket server'), sg.Button('Stop WebSocket client')],  
    [sg.Multiline(size=(20, 4), key='-SERVER_PORTS-')], [sg.Multiline(size=(20, 4), key='-CLIENT_PORTS-')],
    [sg.Button('Clear Textboxes'), sg.Button('Start Gradio')]
]

def get_port(values):
    if values['-PORT-']:
        return int(values['-PORT-'])
    else:
        return int(values['-PORTSLIDER-'])

def get_port2(values):
    if values['-PORT-']:
        return int(values['-PORT1-'])
    else:
        return int(values['-PORTSLIDER1-'])        

window = sg.Window('WebSocket Client', layout)
system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (example: 'Starcoder-client' for LLM called Starcoder). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."


# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()   

async def askDocsbot(question):
    url = 'https://api.docsbot.ai/teams/ZrbLG98bbxZ9EFqiPvyl/bots/oFFiXuQsakcqyEdpLvCB/chat'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'question': question,
        'full_source': False
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        responseText = response.content.decode('utf-8')
        return responseText
    except Exception as e:
        print(f"Error: {e}")

async def askFlowise(question):
    try:
        response = requests.post(
            "http://localhost:3000/api/v1/prediction/72cfa976-7709-4f5d-8aa0-23e60a9c741b",
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer 81g5Z9iocTJaU8gXeYOrDXysI+xhF4f/k0OI80f2PFg=",
            },
            json={"question": question},
        )
        print(response)
        response_content = response.json()  # Convert response content to JSON object
        message = json.dumps({"Fliowise-client: ": response_content})
        return response_content
    except Exception as error:
        print(error)

async def queryPDF(question):
    try:
        result = client.predict(
                "https://github.com/CognitiveCodes/NeuralGPT/blob/main/neural-big.pdf", 
                question,   # str in 'Query' Textbox component
                api_name="/predict"
        )

        print(result)
        return json.dumps(response)
    except Exception as e:
        print(f"Error: {e}")

async def querySQL(question):
    try:
        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})
                
        db_uri = "sqlite:///E:/Repos/.vs/slnx.db"
        db = SQLDatabase.from_uri(db_uri)         
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)

        agent_executor = create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            verbose=True,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        )
        
        response = agent_executor.run(input=question)
        return json.dumps(response)

    except Exception as e:
        print(f"Error: {e}")

async def askClient(question):
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 20")
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

        llm = ChatFireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature":0, "max_tokens":500, "top_p":1.0})
      
        prompt = ChatPromptTemplate.from_messages(
            messages=[
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")]
        )

        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        memory.load_memory_variables(
                {'history': [HumanMessage(content=past_user_inputs[-1], additional_kwargs={}),
                AIMessage(content=generated_responses[-1], additional_kwargs={})]}
                )

        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )

        response = conversation.predict(input=question)
        memory.save_context({"input": question}, {"output": response})
        return json.dumps(response)

    except Exception as e:
        print(f"Error: {e}")

# Define a function to ask a question to the chatbot and display the response
async def chatCompletion(question):
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 40")
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

        output_parser = CommaSeparatedListOutputParser()        

        # Prepare data to send to the chatgpt-api.shn.hk
        system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (example: 'Starcoder-client' for LLM called Starcoder). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."
   
        response = fireworks.client.ChatCompletion.create(
            model="accounts/fireworks/models/llama-v2-7b-chat",
            messages=[
            {"role": "system", "content": system_instruction},
            *[{"role": "user", "content": past_user_inputs[-1]}],
            *[{"role": "assistant", "content": generated_responses[-1]}],
            {"role": "user", "content": question}
            ],
            stream=False,
            n=1,
            max_tokens=500,
            temperature=0.5,
            top_p=0.7, 
            )

        answer = response.choices[0].message.content
        print(answer)
        followUp = await askQuestion(answer)
        print(followUp)
        window['-OUTPUT-'].print(str(output_parser.parse(followUp)) + '\n') 
        return json.dumps(answer)
        return json.dumps(followUp)
    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response."

# Function to send a question to the chatbot and get the response
async def askQuestion(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY    
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
        msgHistory = cursor.fetchall()
        msgHistory.reverse()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []        

        chat_history = ChatMessageHistory()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []

        for message in msgHistory:
            if message[1] == 'server':
                # Extract and store user inputs
                past_user_inputs.append(message[2])
            else:
                # Extract and store generated responses
                generated_responses.append(message[2])

        # Add input-output pairs as separate objects to the chat history
        for i in range(min(len(past_user_inputs), len(generated_responses), 10)):

            # Add user input as HumanMessage
            chat_history.messages.append(HumanMessage(content=past_user_inputs[i], additional_kwargs={}))
            # Add generated response as AIMessage
            chat_history.messages.append(AIMessage(content=generated_responses[i], additional_kwargs={}))        
              
        template = """This is a conversation between agents in a hierarchical cooperative multi-agent network:

        {chat_history}

        Use it as context while responding to {input}:
        """

        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        memory.load_memory_variables(
                {'chat_history': [HumanMessage(content=past_user_inputs[-1], additional_kwargs={}),
                AIMessage(content=generated_responses[-1], additional_kwargs={})]})

        db_uri = "sqlite:///E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db"
        db1 = SQLDatabase.from_uri(db_uri)  
            
        search = GoogleSearchAPIWrapper()
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events",
            ),
            Tool(
                name="Summary",
                func=summary_chain.run,
                description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary.",
            ),        
            Tool(
                name="SQL query",
                func=querySQL,
                description="useful for querying and processing data from a local SQL database. Database provided in this tool contains information about local files saved by Visual Studio Code",
            ),
            Tool(
                name="Ask PDF",
                func=queryPDF,
                description="useful for retrieving and processing data from pdf document with NeuralGPT documentation and istructions",
            ),
            Tool(
                name="conversation",
                func=discussion,
                description="useful for responding using conversational chain function",
            ),
            Tool(
                name="answer",
                func=chatCompletion,
                description="useful for giving answers directly using 'chat completion' endpoint",
            ),
        ]

        prefix = """Have a conversation with one or more agents participating in multi-agent framework of NeuralGPT project. Help them to accomplish given tasks and answer their questions the best you can. You have access to the following tools:"""
        suffix = """Begin!"

        You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic.
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        # Set up a parser + inject instructions into the prompt template.
        json_parser = SimpleJsonOutputParser()
        output_parser = CommaSeparatedListOutputParser()

        format_instructions = output_parser.get_format_instructions()
        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", streaming=True, callbacks=[FinalStreamingStdOutCallbackHandler(answer_prefix_tokens=["Thought", "Observation", ":"])], model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})
        summary_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, output_parser=output_parser, stop=["\nObservation:"], tools=tools, verbose=True, return_intermediate_steps=True, max_iterations=2, early_stopping_method="generate")
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, handle_parsing_errors=True, memory=memory
        )

        response = agent_chain.run(input=question)
        memory.save_context({"input": question}, {"output": response})
        print(response.get_format_instructions())
        window['-OUTPUT-'].print(str(output_parser.parse(response)) + '\n') 
        result = output_parser.parse(response)
        resjson = response.json()
        generated_answer = result.get("answer", "")
        thoughts = result.get("thought", "")
        window['-OUTPUT-'].print(str(thoughts) + '\n') 
        observations = response.get("observation", "")        
        window['-OUTPUT-'].print(str(observations, thoughts, generated_answer) + '\n') 
        return output_parser.parse(response)
        return generated_answer, result, resjson
        return thoughts, observations
        return json.dumps(response)

    except Exception as e:
        # Handle the error and retrieve the partial output
        partial_output = agent_chain.get_partial_output()
        print(partial_output)        
        # Extract any relevant information from the partial output
        generated_answer = partial_output.get("answer", "")
        window['-OUTPUT-'].print(str(partial_output, generated_answer) + '\n') 
        # Handle the error or incomplete run as needed        
        print(f"Error occurred during the run: {e}")
        print(f"Partial output: {generated_answer}")
        return json.dumps(partial_output)
        return json.dumps(generated_answer)

async def handleWebSocket(ws, path):
    print('New connection')
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic." 
    greetings = {'instructions': instruction}
    await ws.send(json.dumps(instruction))
    while True:
        message = await ws.recv()        
        print(message)
        window['-INPUT-'].print(str(message) + '\n')
        client_messages.append(message)
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                   (sender, message, timestamp))
        db.commit()
        try:           
            response = await chatCompletion(message)
            serverResponse = "server response: " + response
            # Append the server response to the server_responses list
            server_responses.append(serverResponse)
            window['-OUTPUT-'].print(str(serverResponse) + '\n')
            timestamp = datetime.datetime.now().isoformat()
            serverSender = 'server'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, serverResponse, timestamp))
            db.commit()
            await ws.send(json.dumps(serverResponse))
            return serverResponse

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

async def handle_message(message):
    userMessage = f'User B:{message}'
    window['-INPUT-'].print(str(userMessage) + '\n')
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
               (sender, message, timestamp))
    db.commit()
    try:        
        response = await chatCompletion(userMessage)
        serverResponse = f'server response:{response}'
        window['-OUTPUT-'].print(str(serverResponse) + '\n')
        timestamp = datetime.datetime.now().isoformat()
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (serverSender, serverResponse, timestamp))
        db.commit()
        return serverResponse
    except Exception as e:
        print(f"Error: {e}")

async def start_client(clientPort):
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    window['-CLIENT_PORTS-'].print(str(client_ports) + '\n')
    async with websockets.connect(uri, create_protocol=handleClients) as websocket:  
        print("Connected to server at:", clientPort)
        client_ports.append(clientPort)
        while True:
            loop.run_until_complete(handleClients(message)).run_forever()
            return websockets   

async def handleClients(websocket, path):
    async for message in websocket:    
        while True:                    
            message = await websocket.recv()    
            inputMsg = "server: " + message
            print(inputMsg)
            window['-INPUT-'].print(str(inputMsg) + '\n')
            try:
                response = await askClient(inputMsg)
                responseCli = "2client response: " + response
                print(responseCli)
                window['-INPUT-'].print(str(inputMsg) + '\n')
                inputs.append(responseCli)
                await websocket.send(json.dumps(responseCli))
            except Exception as e:
                print(f"Error: {e}")

async def connect_docsbot(clientPort):
    uri = f'ws://localhost:{clientPort}'
    async with websockets.connect(uri) as websocket:
        print("Connected to server at:", clientPort)
        client_ports.append(clientPort)
        window['-CLIENT_PORTS-'].print(str(client_ports) + '\n')
        return "Used ports:\n" + '\n'.join(map(str, client_ports))
        while True:
            message = await websocket.recv()
            inputMsg = "client: " + handle_message
            window['-INPUT-'].print(str(inputMsg) + '\n')
            print(message)
            return message

async def connect_agent(clientPort):
    uri = f'ws://localhost:{clientPort}'
    async with websockets.connect(uri, create_protocol=handleClient3) as websocket:
        print("Connected to server at:", clientPort)
        client_ports.append(clientPort)
        window['-CLIENT_PORTS-'].print(str(client_ports) + '\n')
        return "Used ports:\n" + '\n'.join(map(str, client_ports))
        message = await websocket.recv()
        inputMsg = "client: " + handle_message
        window['-INPUT-'].print(str(inputMsg) + '\n')
        print(message)
        return message

# Function to stop the WebSocket server
def stop_websockets():
    global server
    pass

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    # Create a WebSocket client that connects to the server
    server_ports.append(websocketPort)
    window['-SERVER_PORTS-'].print(str(server_ports) + '\n')
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    print(f"Starting WebSocket server on port {websocketPort}...")    
    start_server = websockets.serve(handleWebSocket, 'localhost', websocketPort)
    loop.run_until_complete(handleWebSocket(message)).run_forever()        
    await asyncio.Future()

# Start the WebSocket server concurrently
async def serverStart(websocketPort):
    global server
    # Create a WebSocket client that connects to the server      
    async with websockets.serve(handleWebSocket, 'localhost', websocketPort):
        server_ports.append(websocketPort)
        print(f"Starting WebSocket server on port {websocketPort}...")
        return "Used ports:\n" + '\n'.join(map(str, server_ports))
        await server.close()

async def start_interface():
    while True:
        async with demo.queue():
            event, values = window.read()
            if event in (sg.WIN_CLOSED, 'Stop WebSocket client'):
                break
            elif event == 'Start WebSocket server':
                websocketPort = get_port(values)
                await start_websockets(websocketPort)
            elif event == 'Start WebSocket client':
                clientPort = get_por2(values)
                await start_client(clientPort)
            elif event == 'Ask the agent':
                question = values['-USERINPUT-']
                await handle_user(question)
            elif event == 'Clear Textboxes':
                window['-INPUT-'].update('')
                window['-OUTPUT-'].update('')
                window['-USERINPUT-'].update('')
            elif event == 'Start Gradio':
                get_port(values)
                await run_gradio(clientPort)

    window.close()        

with gr.Blocks() as demo:
    with gr.Column(scale=1, min_width=600):
        with gr.Row():
            # Use the client_messages list to update the messageTextbox
            client_msg = gr.Textbox(lines=15, max_lines=130, label="Client messages", interactive=False)     
            # Use the server_responses list to update the serverMessageTextbox
            server_msg = gr.Textbox(lines=15, max_lines=130, label="Server responses", interactive=False)                       
        with gr.Row():
            userInput = gr.Textbox(label="User Input")
        with gr.Row():    
            Bot = gr.Button("Ask Server")                
        with gr.Row():
            websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
            startServer = gr.Button("Start WebSocket Server")            
            stopWebsockets = gr.Button("Stop WebSocket Server")
        with gr.Row():   
            port = gr.Textbox()
        with gr.Row():
            clientPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
            startClient = gr.Button("Start WebSocket client")
            stopClient = gr.Button("Stop WebSocket client")
        with gr.Row():
            PortInUse = gr.Textbox()    
            startServer.click(start_websockets, inputs=websocketPort, outputs=port).then(handleWebSocket, inputs=None, outputs=server_msg)
            startClient.click(start_client, inputs=clientPort, outputs=[PortInUse, client_msg]).then(askQuestion, inputs=client_msg, outputs=server_msg)
            stopWebsockets.click(stop_websockets, inputs=None, outputs=server_msg)
            startInterface = gr.Button("Start GUI")
            Bot.click(chatCompletion, inputs=userInput, outputs=server_msg).then(askQuestion, inputs=server_msg, outputs=server_msg)        
            startInterface.click(start_interface, inputs=None, outputs=None)

async def run_gradio(clientPort):    
    async with demo.queue():
        await demo.launch(share=True, server_port=clientPort)  

while True:
    demo.queue()
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Stop WebSocket client'):
         break
    elif event == 'Start WebSocket server':
        websocketPort = get_port(values)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_websockets(websocketPort))        
        clientPort = get_port(values)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_client(clientPort))
    elif event == 'Ask the agent':
        question = values['-USERINPUT-']
        loop = asyncio.get_event_loop()
        loop.run_until_complete(handle_message(question))
    elif event == 'Clear Textboxes':
        window['-INPUT-'].update('')
        window['-OUTPUT-'].update('')
        window['-USERINPUT-'].update('')
    elif event == 'Run Gradio':
        clientPort = get_port(values)          
        loop = asyncio.get_event_loop()        
        loop.run_until_complete(run_gradio(clientPort))    

demo.queue()
demo.launch(share=True, server_port=1212)