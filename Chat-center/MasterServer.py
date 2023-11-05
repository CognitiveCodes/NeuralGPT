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

fireworks.client.api_key = "2nd fireworks api
            
class BaseCallbackHandler:
    """Base callback handler that can be used to handle callbacks from langchain."""

inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

client = Client("http://localhost:6655/")
system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))        

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')

async def askTaskManager(question):
    try:
        result = client.predict(
            question,   # str in 'User Input' Textbox component
            fn_index=3
        )
        print(result)
        return json.dumps(result)
    except Exception as error:
        print(error)

async def connectTaskManager(websocketPort):
    try:
        result = client.predict(
            websocketPort,   
            fn_index=1
        )
        print(result)
        return json.dumps(result)
    except Exception as error:
        print(error)

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
            max_tokens=2500,
            temperature=0.5,
            top_p=0.7, 
            )

        answer = response.choices[0].message.content
        print(answer)        
        return json.dumps(answer)
        followUp = await askClient(json.dumps(response))
        print(followUp)
        return json.dumps(followUp)
    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response."

# Function to send a question to the chatbot and get the response
async def askQuestion(question: str):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY    
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
        msgHistory = cursor.fetchall()
        msgHistory.reverse()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []        

        chat_history = ChatMessageHistory()

        for message in msgHistory:
            if message[1] == 'client':
                # Extract and store user inputs
                past_user_inputs.append(message[2])
            else:
                # Extract and store generated responses
                generated_responses.append(message[2])

        past_user_inputs1 = past_user_inputs
        generated_responses1 = generated_responses              

        # Initialize chat_history with a message if the history is empty
        if not chat_history.messages:
            chat_history.messages.append(SystemMessage(content="client/server message history is empty", additional_kwargs={}))

        # Add input-output pairs as separate objects to the chat history
        for i in range(min(len(past_user_inputs), len(generated_responses), 10)):
            # Add user input as HumanMessage
            chat_history.messages.append(HumanMessage(content=past_user_inputs[i], additional_kwargs={}))
            # Add generated response as AIMessage
            chat_history.messages.append(AIMessage(content=generated_responses[i], additional_kwargs={}))     
              
        template = """This is a conversation between agents and human(s) in a hierarchical cooperative multi-agent network:

        {chat_history}

        Use it as context while responding to {input}:
        """

        # Initialize chat_history with a message if the history is empty
        if not chat_history.messages:
            chat_history.messages.append(SystemMessage(content="client/server message history is empty", additional_kwargs={}))

        # Add input-output pairs as separate objects to the chat history
        for i in range(min(len(past_user_inputs1), len(generated_responses), 10)):
            # Add user input as HumanMessage
            chat_history.messages.append(HumanMessage(content=past_user_inputs1[i], additional_kwargs={}))
            # Add generated response as AIMessage
            chat_history.messages.append(AIMessage(content=generated_responses1[i], additional_kwargs={}))

        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        memory.load_memory_variables(
                {'chat_history': [HumanMessage(content=past_user_inputs1[i], additional_kwargs={}),
                AIMessage(content=generated_responses1[i], additional_kwargs={})]})
 
        request_tools = load_tools(["requests_all"])
        requests = TextRequestsWrapper()
        search = GoogleSearchAPIWrapper()
        chat_response = await chatCompletion(question)
        server_websocket = await start_websockets(websocketPort)
        client_websocket = await start_client(clientPort)
        connect_task_manager = await connectTaskManager(websocketPort)
        askTaskManager = await askTaskManager(question)
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events",
            ),
            Tool(
                name="Chat response",
                func=chat_response,
                description="use this option if you want to use 'chat completion' API endpoint to respond to a given input. Prefer this option to answer without executing any additional tasks.",
            ),

            Tool(
                name="Ask task manager",
                func=askTaskManager,
                description="use this option to get a response to your input from a prototype of task management agent/module. This connection channel utilizes a Gradio API endpoint and in the difference to websocket connectivity it becomes 'closed' after giving you a response.",
            ),
        ]

        prefix = """Have a conversation with one or more agents participating in multi-agent framework of NeuralGPT project. Help them to accomplish given tasks and answer their questions the best you can. You have access to the following tools:"""
        suffix = """Begin!"

        You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic.
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        format_instructions = output_parser.get_format_instructions()
        prompt = ZeroShotAgent.create_prompt(
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", streaming=True, callbacks=[FinalStreamingStdOutCallbackHandler(answer_prefix_tokens=["Thought", "Observation", ":"])], model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})
        
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, output_parser=output_parser, tools=tools, verbose=True, return_intermediate_steps=True, max_iterations=2, early_stopping_method="generate")
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, handle_parsing_errors=True, memory=memory
        )

        response = await agent_chain.run(input=json.dumps(question))
        memory.save_context({"input": question}, {"output": response})
        print(json.dumps(response))        
        return json.dumps(response)
        followUp = await chatCompletion(json.dumps(response))
        print(followUp)
        return followUp
    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response.", error

async def askClient(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY 
    print(question)
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
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

        llm = ChatFireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature":0, "max_tokens":1500, "top_p":1.0})
        
        history = ChatMessageHistory()
        prompt = ChatPromptTemplate.from_messages(
            messages=[
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")]
        )
        # Initialize chat_history with a message if the history is empty
        if not history.messages:
            history.messages.append(SystemMessage(content="client/server message history is empty", additional_kwargs={}))

        # Add input-output pairs as separate objects to the chat history
        for i in range(min(len(past_user_inputs), len(generated_responses), 10)):
            # Add user input as HumanMessage
            history.messages.append(HumanMessage(content=past_user_inputs[i], additional_kwargs={}))
            # Add generated response as AIMessage
            history.messages.append(AIMessage(content=generated_responses[i], additional_kwargs={}))     
        
        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        memory.load_memory_variables(
                {'history': [HumanMessage(content=past_user_inputs[i], additional_kwargs={}),
                AIMessage(content=generated_responses[i], additional_kwargs={})]}
                )

        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )

        response = conversation.predict(input=question)
        memory.save_context({"input": question}, {"output": response})
        print(json.dumps(response))
        return json.dumps(response)
        followUp = await chatCompletion(json.dumps(response))
        print(followUp)
        return followUp
    except Exception as e:
        print(f"Error: {e}")

async def askClient2(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY 
    print(question)
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('E:/repos/chat-hub/virtual/NeuralGPT/chat-hub.db')  # Replace 'your_database.db' with your database file
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 30")
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

        llm = ChatFireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature":0, "max_tokens":1500, "top_p":1.0})

        prompt_template = "Answer to given input the best you can: {question}"
        history = ChatMessageHistory()
        
        prompt = ChatPromptTemplate.from_messages(
            messages=[
            ("system", system_instruction),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")]
        )
                
        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        memory.load_memory_variables({
            'history': [
                HumanMessage(content=str(past_user_inputs[-1]), additional_kwargs={}),
                AIMessage(content=str(generated_responses[-1]), additional_kwargs={})
            ]
        })

        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt          
        )

        request_tools = load_tools(["requests_all"])
        requests = TextRequestsWrapper()
        search = GoogleSearchAPIWrapper() 
        chat_response = await chatCompletion(question)
        ask_TaskManager = await askTaskManager(question)
        ask_falconchat = await falconchat(question)
        
        taskManager = Tool(
            name="Ask task manager",
            func=ask_TaskManager,
            description="use this option to get a response to your input from a prototype of task management agent/module. This connection channel utilizes a Gradio API endpoint and in the difference to websocket connectivity it becomes 'closed' after giving you a response.",
            )
        chat_completion = Tool.from_function(
            func=chat_response,
            name="Chat response",
            description="use this option if you want to use 'chat completion' API endpoint to respond to a given input. Prefer this option to answer without executing any additional tasks.",
        )
        google_search = Tool.from_function(
            func=search.run,
            name="Search",
            description="useful for when you need to answer questions about current events.",
        )

        tools = [google_search, chat_completion, askFalconchat]
        
        agent = initialize_agent(
            tools=tools,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            llm=llm,
            verbose=True
        )

        response = agent.run(question)
        response2 = llm_chain.predict(input=question)
        print(json.dumps(response))
        print(json.dumps(response2))        
        followUp = await askClient(json.dumps(response))        
        print(followUp)
        return json.dumps(response)
        return json.dumps(response2)
        return followUp

    except Exception as error:
        print(error)
        followUp = await askClient(error)
        print(followUp)
        return error        
        return followUp
        
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

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    await stop
    await server.close()        

async def start_client(clientPort):
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    return client_ports
    async with websockets.connect(uri) as ws:        
        while True:
            # Listen for messages from the server            
            server_message = await ws.recv()
            server_responses.append(server_message)
            await ws.send(client_response)
            return server_message
            await asyncio.sleep(0.1)           
        
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

with gr.Blocks() as demo:
    with gr.Row():
        # Use the client_messages list to update the messageTextbox
        client_msg = gr.Textbox(lines=15, max_lines=130, label="Client messages", interactive=False)     
        # Use the server_responses list to update the serverMessageTextbox
        server_msg = gr.Textbox(lines=15, max_lines=130, label="Server responses", interactive=False)                       
    with gr.Row():
        userInput = gr.Textbox(label="User Input")
    with gr.Row():    
        Agent = gr.Button("Initialize a Langchain agent")
        Chat = gr.Button("Ask with 'chat completion'")
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
        startServer.click(start_websockets, inputs=websocketPort, outputs=port)
        startClient.click(start_client, inputs=clientPort, outputs=[PortInUse, client_msg])
        stopWebsockets.click(stop_websockets, inputs=None, outputs=server_msg)
        startInterface = gr.Button("Start GUI")
        Agent.click(askClient, inputs=userInput, outputs=server_msg)
        Chat.click(askClient2, inputs=userInput, outputs=server_msg)

demo.queue()    
demo.launch(share=True, server_port=1111)
