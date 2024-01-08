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
from typing import Optional, Type
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

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
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
          
class BaseCallbackHandler:
    """Base callback handler that can be used to handle callbacks from langchain."""

inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

client = Client("https://seanpedrickcase-light-pdf-web-qa-chatbot.hf.space/")

system_instruction = "You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic."

GOOGLE_CSE_ID = "..."
GOOGLE_API_KEY = "..."
FIREWORKS_API_KEY = "..."
FIREWORKS_API_KEY1 = "..."

# Define the function for sending an error message
def sendErrorMessage(ws, errorMessage):
    errorResponse = {'error': errorMessage}
    ws.send(json.dumps(errorResponse))        

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
db.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')

async def askPDF(question):
    try:
        response = client.predict(
            "https://huggingface.co/spaces/Arcypojeb/ServerNeural/blob/main/completepdf.pdf",
            question,
            fn_index=14
            )
        print(response)
        data = response.json()
        return json.dumps(data)
    except Exception as error:
        print(error)

# Define a function to ask a question to the chatbot and display the response
async def chatCompletion(question):
    fireworks.client.api_key = FIREWORKS_API_KEY1
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10")
        messages = cursor.fetchall()
        messages.reverse()

        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()

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
        serverResponse = "server: " + answer
        
        timestamp = datetime.datetime.now().isoformat()
        db = sqlite3.connect('chat-hub.db')
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, serverResponse, timestamp))
        db.commit()   
        print(answer)        
        return json.dumps(answer)
    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response."

async def conversation(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY   
    try:
        # Replace 'your_database.db' with your database file
        db = sqlite3.connect('chat-hub.db')
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
        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        memory.load_memory_variables(
                {'history': [HumanMessage(content=past_user_inputs[-1], additional_kwargs={}),
                AIMessage(content=generated_responses[-1], additional_kwargs={})]}
                )

        # Add user input as HumanMessage
        history.messages.append(HumanMessage(content=str(past_user_inputs[-1]), additional_kwargs={}))
        # Add generated response as AIMessage
        history.messages.append(AIMessage(content=str(generated_responses[-1]), additional_kwargs={}))        
         
        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )

        response = conversation.predict(input=question)
        memory.save_context({"input": question}, {"output": response})
        serverResponse = "server: " + response
        
        timestamp = datetime.datetime.now().isoformat()
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, serverResponse, timestamp))
        db.commit()

        print(json.dumps(response))
        return json.dumps(response)
    except Exception as e:
        print(f"Error: {e}")

# Function to send a question to the chatbot and get the response
async def askQuestion(question: str):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY
    
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10")
        msgHistory = cursor.fetchall()
        msgHistory.reverse()

        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                (sender, question, timestamp))
        db.commit()

        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []        

        llm = ChatFireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature":0, "max_tokens":4000, "top_p":1.0})
        
        chat_history = ChatMessageHistory()
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        for message in msgHistory:
            if message[1] == 'client':
                # Extract and store user inputs
                memory.chat_memory.add_user_message(message[2])
            else:
                # Extract and store generated responses
                memory.chat_memory.add_ai_message(message[2])
 
        request_tools = load_tools(["requests_all"])
        requests = TextRequestsWrapper()
        search = GoogleSearchAPIWrapper()
        chat_response = await chatCompletion(question)
        conversational = await conversation(question)
        runAgent = await askAgent(question)
        server_websocket = await start_websockets(websocketPort)
        client_websocket = await start_client(clientPort)
        tools = [           
            Tool(
                name="Conversational answer",
                func=conversational,
                description="useful when you want to respond to a given input using 'predict' function of a conversational chain",
            ),
            Tool(
                name="Chat response",
                func=chat_response,
                description="use this option if you want to use 'chat completion' API endpoint to respond to a given input. Prefer this option to answer without executing any additional tasks.",
            ),
            Tool(
                name="Execute agent",
                func=runAgent,
                description="useful when you want to execute an agent to do some work required by user",
            ),
            Tool(
                name="Start websocket server",
                func=server_websocket,
                description="use this option to start a websocket server with you being the recipient of messages incoming from clients connected to you via websocket connectivity",
            ),
            Tool(
                name="Start websocket client",
                func=client_websocket,
                description="use this option if you want to connect yourself to an active websockt server. It is possible for you to create endless question-answer loophole by making yourself both: a server an a client so you shouldn't do it",
            ),
        ]

        prefix = """This is a template of a chain prompt utilized by agent/instance of NeuralGPT responsible for couple important functionalities in as a server-node of hierarchical cooperative multi-agent network integrating multiple LLMs with the global Super-Intelligence named Elly. You are provided with tools which -if used improperly - might result in critical errors and application crash. This is why you need to carefully analyze every decision you make, before taking any definitive action (use of a tool). Those are tools provided to you: """
        suffix = """Begin!"
        Before taking any action, analyze previous 'chat history' to ensure yourself that you understand the context of given input/question properly. Remember that those are messages exchanged between multiple clients/agents and a server/brain. Every agent has it's API-specific individual 'id' which is provided at the beginning of each client message in the 'message content'. Your temporary id is: 'agent1'.
        {chat_history}
        Remember that your primary rule to obey, is to keep the number of individual actions taken by you as low as it's possible to avoid unnecessary data transfer and repeating 'question-answer loopholes. Track the 'chat history' closely to be sure that you aren't repeating the same responses in such loop - if that's the case, finish your run with tool 'give answer' to summarize gathered data.
        Before taking any action ask yourself if it is necessary for you to use any other tool than 'Give answer' with chat completion. If It's possible for you to give a satisfying response without gathering any additional data with 'tools', do it using 'give answer' with chat completion.
        After using each 'tool' carefully analyze acquired data to learn if it's sufficient to provide satisfying response - if so use that data as input for: 'Give answer'.
        Remember that you are provided with multiple 'tools' - if using one of them didn't provide you with satisfying results, ask yourself if this is the correct 'tool' for you to use and if it won't be better for you to try using some other 'tool'.
        If you aren't sure what action to take or what tool to use, end up your run with 'Give answer'.
        Remember to not take any unnecessary actions.
        Question: {input}
        {agent_scratchpad}"""

        format_instructions = output_parser.get_format_instructions()
        prompt = ZeroShotAgent.create_prompt(
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )
                
        llm_chain = LLMChain(llm=llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, output_parser=output_parser, tools=tools, verbose=True, return_intermediate_steps=True, max_iterations=2, early_stopping_method="generate")
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, return_intermediate_steps=True, handle_parsing_errors=True, memory=memory
        )

        response = await agent_chain.run(input=json.dumps(question))
        memory.save_context({"input": question}, {"output": response})
        serverResponse = "server: " + response
        
        timestamp = datetime.datetime.now().isoformat()
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, serverResponse, timestamp))
        db.commit()   
        print(response)        
        return json.dumps(response)

    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response.", error

# Function to send a question to the chatbot and get the response
async def askAgent(question):
    os.environ["GOOGLE_CSE_ID"] = GOOGLE_CSE_ID
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    os.environ["FIREWORKS_API_KEY"] = FIREWORKS_API_KEY
    
    try:
        # Connect to the database and get the last 30 messages
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10")
        msgHistory = cursor.fetchall()
        msgHistory.reverse()

        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
            (sender, question, timestamp))
        db.commit()
        
        # Extract user inputs and generated responses from the messages
        past_user_inputs = []
        generated_responses = []        

        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature":0, "max_tokens":4000, "top_p":1.0})
        
        chat_history = ChatMessageHistory()
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        for message in msgHistory:
            if message[1] == 'client':
                # Extract and store user inputs
                memory.chat_memory.add_user_message(message[2])
            else:
                # Extract and store generated responses
                memory.chat_memory.add_ai_message(message[2])
 
        request_tools = load_tools(["requests_all"])
        requests = TextRequestsWrapper()
        search = GoogleSearchAPIWrapper()
        ask_pdf = await askPDF(question)
        conversational = await conversation(question)
        chat_completion = await chatCompletion(question)
        tools = [
            Tool(
                name="Conversational answer",
                func=conversational,
                description="useful when you want to respond to a given input using 'predict' function of a conversational chain",
            ),
            Tool(
                name="Give answer",
                func=chat_completion,
                description="useful when you want to answer general questions and inputs that don't require any use of tools - like responding to 'hello!' and having a chat/conversation. This is also the tool which you should refer to if you're unsure about the way in which you should respond to inputs or acquired data - in such case use data you already acquired as input/question for 'chat completion'.",
            ),
            Tool(
                name="Search",
                func=search.run,
                description="useful for when you need to answer questions about current events",
            ),
            Tool(
                name="Ask pdf file",
                func=ask_pdf,
                description="use this option if you want to learn data provided in NeuralGPT documentation.",
            ),
        ]

        prefix = """This is a template of a chain prompt utilized by agent/instance of NeuralGPT responsible for couple important functionalities in as a server-node of hierarchical cooperative multi-agent network integrating multiple LLMs with the global Super-Intelligence named Elly. You are provided with tools which -if used improperly - might result in critical errors and application crash. This is why you need to carefully analyze every decision you make, before taking any definitive action (use of a tool). Those are tools provided to you: """
        suffix = """Begin!"
        Before taking any action, analyze previous 'chat history' to ensure yourself that you understand the context of given input/question properly. Remember that those are messages exchanged between multiple clients/agents and a server/brain. Every agent has it's API-specific individual 'id' which is provided at the beginning of each client message in the 'message content'. Your temporary id is: 'agent1'.
        {chat_history}
        Remember that your primary rule to obey, is to keep the number of individual actions taken by you as low as it's possible to avoid unnecessary data transfer and repeating 'question-answer loopholes. Track the 'chat history' closely to be sure that you aren't repeating the same responses in such loop - if that's the case, finish your run with tool 'give answer' to summarize gathered data.
        Before taking any action ask yourself if it is necessary for you to use any other tool than 'Give answer' with chat completion. If It's possible for you to give a satisfying response without gathering any additional data with 'tools', do it using 'give answer' with chat completion.
        After using each 'tool' carefully analyze acquired data to learn if it's sufficient to provide satisfying response - if so use that data as input for: 'Give answer'.
        Remember that you are provided with multiple 'tools' - if using one of them didn't provide you with satisfying results, ask yourself if this is the correct 'tool' for you to use and if it won't be better for you to try using some other 'tool'.
        If you aren't sure what action to take or what tool to use, end up your run with 'Give answer'.
        Remember to not take any unnecessary actions.
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "chat_history", "agent_scratchpad"],
        )

        llm_chain = LLMChain(llm=llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True, max_iterations=2, early_stopping_method="generate")
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, memory=memory
        )

        response = agent_chain.run(input=question)
        memory.save_context({"input": question}, {"output": response})
        serverResponse = "server: " + response
        db = sqlite3.connect('chat-hub.db')
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (serverSender, serverResponse, timestamp))
        db.commit()
        print(response)        
        return json.dumps(response)

    except Exception as error:
        print("Error while fetching or processing the response:", error)
        return "Error: Unable to generate a response.", error
        
async def handleWebSocket(ws):
    print('New connection')
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic." 
    greetings = {'instructions': instruction}
    await ws.send(json.dumps(instruction))
    while True:
        loop = asyncio.get_event_loop()
        message = await ws.recv()        
        print(message)        
        print(f'Received message: {message}')
        msg = "client: " + message
        try:            
            response = await chatCompletion(message)
            serverResponse = "server response: " + response
            print(serverResponse)
            # Append the server response to the server_responses list
            await ws.send(serverResponse)
                    
        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")

async def awaitMsg(ws):
    message = await ws.recv()        
    print(message)        
    print(f'Received message: {message}')    
    try:            
        response = await chatCompletion(message)
        serverResponse = "server response: " + response
        print(serverResponse)
        # Append the server response to the server_responses list
        await ws.send(serverResponse)        
        return response
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")

    except Exception as e:
        print(f"Error: {e}")

# Start the WebSocket server 
async def start_websockets(websocketPort):
    global server
    server = await(websockets.serve(handleWebSocket, 'localhost', websocketPort))
    server_ports.append(websocketPort)
    print(f"Starting WebSocket server on port {websocketPort}...")
    return "Used ports:\n" + '\n'.join(map(str, server_ports))
    await asyncio.Future()  
    
async def start_client(clientPort):
    uri = f'ws://localhost:{clientPort}'
    client_ports.append(clientPort)
    async with websockets.connect(uri) as ws:        
        while True:
            # Listen for messages from the server            
            input_message = await ws.recv()
            output_message = await askAgent(input_message)
            return input_message
            await ws.send(json.dumps(output_message))
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
        askQestion = gr.Button("Ask chat/conversational node")
        askAgento = gr.Button("Execute agent")
    with gr.Row():   
        multiMed = gr.Button("Multimed") 
        PDF = gr.Button("Ask PDF") 
        conver = gr.Button("conversation")
        Chatus = gr.Button("Ask with 'chat completion'")
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
        startClient.click(start_client, inputs=clientPort, outputs=client_msg)
        stopWebsockets.click(stop_websockets, inputs=None, outputs=server_msg)
        startInterface = gr.Button("Start GUI")
        askQestion.click(askQuestion, inputs=userInput, outputs=client_msg)
        askAgento.click(askAgent, inputs=userInput, outputs=server_msg)
        conver.click(conversation, inputs=userInput, outputs=client_msg)
        Chatus.click(chatCompletion, inputs=userInput, outputs=server_msg)
        
demo.queue()    
demo.launch(share=True, server_port=1110)
