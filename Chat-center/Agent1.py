import datetime
import os
import sqlite3
import websockets
import asyncio
import sqlite3
import json
import requests
import asyncio
import time
import gradio as gr
from gradio_client import Client
from websockets.sync.client import connect

from tempfile import TemporaryDirectory
from langchain import hub
from langchain.utilities import GoogleSearchAPIWrapper
from langchain.chains import LLMChain
from langchain.chains import ConversationChain
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


# Define the global constants for the API keys
GOOGLE_CSE_ID = "<paste CSE ID>"
GOOGLE_API_KEY = "<paste Google API>"
FIREWORKS_API_KEY = "<paste Fireworks API>"
            
os.chdir("path/to/dir")
working_directory = "path/to/dir"

inputs = []
outputs = []
ports = []

# Set up the SQLite database
db = sqlite3.connect('chat-hub.db')
cursor = db.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, message TEXT, timestamp TEXT)')    
db.commit()

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

        for message in msgHistory:
            if message[1] == 'server':
                past_user_inputs.append(message[2])
            else:
                generated_responses.append(message[2])

        chat_history = ""

        for user_input, agent_response in zip(past_user_inputs, generated_responses):
            chat_history += f"Server: {user_input}\nAgent: {agent_response}\n\n"
                
        llm = Fireworks(model="accounts/fireworks/models/llama-v2-13b-chat", model_kwargs={"temperature": 0, "max_tokens": 500, "top_p": 1.0})
                
        template = """This is a conversation between agents in a hierarchical cooperative multi-agent network:

        {chat_history}

        Use it as context while responding to {input}:
        """

        prompt = PromptTemplate(input_variables=["input", "chat_history"], template=template)
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        memory.load_memory_variables(
                {'chat_history': [HumanMessage(content=past_user_inputs[-1], additional_kwargs={}),
                AIMessage(content=generated_responses[-1], additional_kwargs={})]})

        summary_chain = LLMChain(
            llm=llm,
            prompt=prompt,
            verbose=True,
            memory=memory
        )

        sql_query = SQLDatabaseToolkit(db=db, llm=llm(temperature=0))
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
                name="sql_query",
                func=ssql_query.run,
                description="useful for when you summarize a conversation. The input to this tool should be a string, representing who will read this summary.",
            ),
        ] SQLDatabaseToolkit(db=db, llm=llm(temperature=0))
        
        prefix = """Have a conversation with a node of higher hierarchy or user B, answering questions and accomplishing given tasks as best you can. You have access to the following tools:"""
        suffix = """Begin!"

        You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (example: 'Starcoder-client' for LLM called Starcoder). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic.
        {chat_history}
        Question: {input}
        {agent_scratchpad}"""

        prompt = ZeroShotAgent.create_prompt(
            tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["input", "system_instruction", "chat_history", "agent_scratchpad"],
        )

        llm_chain = LLMChain(llm=llm, prompt=prompt)
        agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True)
        agent_chain = AgentExecutor.from_agent_and_tools(
            agent=agent, tools=tools, verbose=True, memory=memory
        )

        response = agent_chain.run(input=question)
        memory.save_context({"input": question}, {"output": response})
        return response["output"], response["intermediate_steps"]     
        response_content = response.content.decode('utf-8')     
        return response, response_content  

    except Exception as e:
        print(f"Error: {e}")

async def start_client(websocketPort):
    uri = f'ws://localhost:{websocketPort}'
    ports.append(websocketPort)
    async with websockets.connect(uri) as ws:
        print("Connected to server at:", websocketPort)
        return ports    
        while True:
            await handle_message(ws, '/')
               
async def handle_message(ws):
    message = await ws.recv()
    print(message)
    response = await askQuestion(message)
    print(response)
    await ws.send(response)            
    
with gr.Blocks() as demo:
    with gr.Row():
        client_message = gr.Textbox(lines=15, max_lines=130, label="Chat", interactive=False)
        server_message = gr.Textbox(lines=15, max_lines=130, label="Chat", interactive=False)
    with gr.Row():
        userInput1 = gr.Textbox(label="User Input")
    with gr.Row():    
        Bot1 = gr.Button("Ask Agent")    
    with gr.Row():
        websocketPort = gr.Slider(minimum=1000, maximum=9999, label="Websocket server port", interactive=True, randomize=False)
        startWebsockets = gr.Button("Start WebSocket client")            
        stopWebsockets = gr.Button("Stop WebSocket client")
    with gr.Row():   
        ports = gr.Textbox()  
        Bot1.click(askQuestion, inputs=userInput1, outputs=server_message)
        startWebsockets.click(start_client, inputs=websocketPort, outputs=server_message)

demo.queue()    
demo.launch(share=True, server_port=1118)
