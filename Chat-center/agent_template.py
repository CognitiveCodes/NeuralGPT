import datetime
import os
import sqlite3
import websockets
import websocket
import asyncio
import sqlite3
import json
import logging
import requests
import asyncio
import time
import gradio as gr
import fireworks.client
import PySimpleGUI as sg
from gradio_client import Client
from bs4 import BeautifulSoup
from pathlib import Path
from langchain.utilities import TextRequestsWrapper
from langchain.agents import load_tools
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
from langchain.utilities import TextRequestsWrapper
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
FIREWORKS_API_KEY = "fireworks api"

fireworks.client.api_key = "2nd fireworks api"
            
os.chdir("E:/repos/chat-hub/virtual/NeuralGPT")
working_directory = "E:/repos/chat-hub/virtual/NeuralGPT"

class BaseCallbackHandler:
    """Base callback handler that can be used to handle callbacks from langchain."""

inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

client = Client("https://huggingfaceh4-falcon-chat.hf.space/")

async def querySQLfilesystem():
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

async def querySQLchat(question):
    try:
        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})
                
        db_uri = "sqlite:///E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db"
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

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))        

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')

async def falconchat(question):
    try:
        result = client.predict(
                question,   # str  in 'Click on any example and press Enter in the input textbox!' Dataset component
                fn_index=0
        )
        print(result)
        return json.dumps(result)
    except Exception as error:
        print(error)

# Define the function for asking a question to the chatbot
async def getTasks(projectId):
    url = f'https://www.taskade.com/api/v1/projects/{projectId}/tasks?limit=10'
    headers = {'Authorization': 'Bearer tskdp_r7hHhe7rAcVPyxLkdwf3Me9zimiWekjFke'}
    try:      
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        return json.dumps(data)
    except Exception as error:
        print(error)      

# Define the function for handling incoming messages
async def getProjects():
    url = 'https://www.taskade.com/api/v1/me/projects?limit=100&page=1&sort=viewed-desc'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer tskdp_r7hHhe7rAcVPyxLkdwf3Me9zimiWekjFke'
    }
    try:      
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        return json.dumps(data)
    except Exception as error:
        print(error)

async def getworkspaces():
    url = 'https://www.taskade.com/api/v1/workspaces'
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer tskdp_r7hHhe7rAcVPyxLkdwf3Me9zimiWekjFke'
    }    
    try:      
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        return json.dumps(data)
    except Exception as error:
        print(error)

# Define the function for asking a question to the chatbot
async def getFolders():
    url = 'https://www.taskade.com/api/v1/workspaces/bx1Ka2nFFXjiUPSW/folders'
    headers = {'Authorization': 'Bearer tskdp_r7hHhe7rAcVPyxLkdwf3Me9zimiWekjFke'}
    try:      
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        return json.dumps(data)
    except Exception as error:
        print(error)

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

        # Add user input as HumanMessage
        chat_history.messages.append(HumanMessage(content=str(past_user_inputs[-1]), additional_kwargs={}))
        # Add generated response as AIMessage
        chat_history.messages.append(AIMessage(content=str(generated_responses[-1]), additional_kwargs={}))        
              
        template = """

        {chat_history}

        Use it as context while responding to {input}:
        """

        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        memory.load_memory_variables(
                {'chat_history': [HumanMessage(content=str(past_user_inputs[-1]), additional_kwargs={}),
                AIMessage(content=str(generated_responses[-1]), additional_kwargs={})]})
 
        request_tools = load_tools(["requests_all"])
        requests = TextRequestsWrapper()
        search = GoogleSearchAPIWrapper()
        getworspaces = await getworkspaces()
        getprojects = await getProjects()
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events",
            ),
        ]

        prefix = """This is a template of a chain prompt utilized by agent/instnce responsible for proper functioning task management departament in a hierarchical cooperative multi-agent gramework named NeuralGPT. You are provided with the following tools designed to operate on Tassk flows within the frame of NeuralGPT project :"""
        suffix = """Begin!"

        You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic.
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

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
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True, max_iterations=2, early_stopping_method="generate")
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, memory=memory
        )

        response = agent_chain.run(input=question)
        memory.save_context({"input": question}, {"output": response})
        print(response)        
        return json.dumps(response)

    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response.", error

# Define the WebSocket handler
async def handleWebSocket(ws, path):
    print('New connection')
    try:
        await ws.send('Hello! Please integrate yourself with the local sql database and file system')
        async for message in ws:
            print(f'Received message: {message}')            
            parsedMessage = json.loads(message)
            messageText = parsedMessage.get('text', '')
            timestamp = datetime.datetime.now().isoformat()
            sender = 'client'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)', (sender, messageText, timestamp))
            db.commit()
            try:
                if 'text' in parsedMessage:
                    answer = await askQuestion(parsedMessage['text'])
                    response = {'answer': answer}
                    await ws.send(json.dumps(response))                    
                    serverMessageText = response.get('answer', '')
                    serverSender = 'server'
                    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)', (serverSender, serverMessageText, timestamp))
                    db.commit()
            except Exception as e:
                print(e)
                sendErrorMessage(ws, 'An error occurred while processing the message.')
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Closing connection")
        
# Function to stop the WebSocket server
def stop_websockets():
    global server
    if server:
        cursor.close()
        db.close()
        server.close()
        print("WebSocket server stopped.")
    else:
        print("WebSocket server is not running.")   

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    # Create a WebSocket client that connects to the server    
      
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    await stop
    await server.close()

async def start_client(clientPort):
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    async with websockets.connect(uri) as websocket:  
        print("Connected to server at:", clientPort)
        while True:
            message = await websocket.recv()
            inputMsg = "server: " + message
            print(inputMsg)
            try:
                response = await askQuestion(inputMsg)
                responseCli = "client response: " + response
                print(responseCli)
                inputs.append(responseCli)
                await websocket.send(json.dumps(responseCli))
            except Exception as e:
                print(f"Error: {e}")

with gr.Blocks() as demo:
    with gr.Row():
        # Use the client_messages list to update the messageTextbox
        client_msg = gr.Textbox(lines=15, max_lines=130, label="Client messages", interactive=False)     
        # Use the server_responses list to update the serverMessageTextbox
        server_msg = gr.Textbox(lines=15, max_lines=130, label="Server responses", interactive=False)                       
    with gr.Row():
        userInput = gr.Textbox(label="User Input")
    with gr.Row():    
        Bot = gr.Button("Ask Server")
        tool = gr.Button("Test a tool")
    with gr.Row():
        websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
        startServer = gr.Button("Start WebSocket Server")            
        stopWebsockets = gr.Button("Stop WebSocket Server")
    with gr.Row():   
        port = gr.Textbox()
    with gr.Row():
        clientPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket client port", interactive=True, randomize=False)
        startClient = gr.Button("Start WebSocket client")
        stopClient = gr.Button("Stop WebSocket client")
    with gr.Row():
        PortInUse = gr.Textbox()    
        startServer.click(start_websockets, inputs=websocketPort, outputs=port)
        startClient.click(start_client, inputs=clientPort, outputs=[PortInUse, client_msg])
        stopWebsockets.click(stop_websockets, inputs=None, outputs=server_msg)
        startInterface = gr.Button("Start GUI")
        Bot.click(askQuestion, inputs=userInput, outputs=server_msg)
        tool.click(querySQLchat, inputs=userInput, outputs=server_msg)

demo.queue()    
demo.launch(share=True, server_port=6655)
