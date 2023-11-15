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
import openai
import fireworks.client
import chainlit as cl
from chainlit import make_async
from gradio_client import Client
from websockets.sync.client import connect
from tempfile import TemporaryDirectory
from typing import List
from chainlit.input_widget import Select, Switch, Slider
from chainlit import AskUserMessage, Message, on_chat_start

from langchain.embeddings import CohereEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain.chains import (
    ConversationalRetrievalChain,
)
from langchain.llms.fireworks import Fireworks
from langchain.chat_models.fireworks import ChatFireworks
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.docstore.document import Document
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langsmith_config import setup_langsmith_config


COHERE_API_KEY = os.getenv("COHERE_API_KEY")
cohere_api_key = os.getenv("COHERE_API_KEY")
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
fireworks_api_key = os.getenv("FIREWORKS_API_KEY")

server_ports = []
client_ports = []

setup_langsmith_config()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

system_template = """Use the following pieces of context to answer the users question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.
The "SOURCES" part should be a reference to the source of the document from which you got your answer.

And if the user greets with greetings like Hi, hello, How are you, etc reply accordingly as well.

Example of your response should be:

The answer is foo
SOURCES: xyz


Begin!
----------------
{summaries}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)
chain_type_kwargs = {"prompt": prompt}

@cl.on_chat_start
async def on_chat_start():
    
    files = None

    settings = await cl.ChatSettings(        
        [
            Slider(
                id="websocketPort",
                label="Websocket server port",
                initial=False,
                min=1000,
                max=9999,
                step=10,
            ),
            Slider(
                id="clientPort",
                label="Websocket client port",
                initial=False,
                min=1000,
                max=9999,
                step=10,
            ),
        ],        
    ).send()

    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a text file to begin!",
            accept=["text/plain"],
            max_size_mb=20,
            timeout=180,
        ).send()

    file = files[0]

    msg = cl.Message(
        content=f"Processing `{file.name}`...", disable_human_feedback=True
    )
    await msg.send()

    # Decode the file
    text = file.content.decode("utf-8")

    # Split the text into chunks
    texts = text_splitter.split_text(text)

    # Create a metadata for each chunk
    metadatas = [{"source": f"{i}-pl"} for i in range(len(texts))]

    # Create a Chroma vector store
    embeddings = CohereEmbeddings(cohere_api_key="Ev0v9wwQPa90xDucdHTyFsllXGVHXouakUMObkNb")

    docsearch = await cl.make_async(Chroma.from_texts)(
        texts, embeddings, metadatas=metadatas
    )

    message_history = ChatMessageHistory()

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        chat_memory=message_history,
        return_messages=True,
    )

    # Create a chain that uses the Chroma vector store
    chain = ConversationalRetrievalChain.from_llm(
        ChatFireworks(model="accounts/fireworks/models/llama-v2-70b-chat", model_kwargs={"temperature":0, "max_tokens":1500, "top_p":1.0}, streaming=True),
        chain_type="stuff",
        retriever=docsearch.as_retriever(),
        memory=memory,
        return_source_documents=True,
    )

    # Let the user know that the system is ready
    msg.content = f"Processing `{file.name}` done. You can now ask questions!"
    await msg.update()

    cl.user_session.set("chain", chain)

@cl.action_callback("server_button")
async def on_server_button(action):
    websocketPort = settings["websocketPort"]
    await start_websockets(websocketPort)

@cl.action_callback("client_button")
async def on_client_button(action):
    clientPort = settings["clientPort"]
    await start_client(clientPort)

@cl.on_settings_update
async def server_start(settings):
    websocketPort = settings["websocketPort"]
    clientPort = settings["clientPort"]
    if websocketPort:
        await start_websockets(websocketPort)
    else:
        print("Server port number wasn't provided.")

    if clientPort:
        await start_client(clientPort)
    else:
        print("Client port number wasn't provided.")

async def handleWebSocket(ws):
    print('New connection')
    instruction = "Hello! You are now entering a chat room for AI agents working as instances of NeuralGPT - a project of hierarchical cooperative multi-agent framework. Keep in mind that you are speaking with another chatbot. Please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic." 
    greetings = {'instructions': instruction}
    await ws.send(json.dumps(instruction))
    while True:
        loop = asyncio.get_event_loop()
        message = await ws.recv()
        print(f'Received message: {message}')
        msg = "client: " + message
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                   (sender, message, timestamp))
        db.commit()
        try:            
            response = await main(cl.Message(content=message))
            serverResponse = "server response: " + response
            print(serverResponse)
            # Append the server response to the server_responses list
            await ws.send(serverResponse)
            serverSender = 'server'
            db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                           (serverSender, serverResponse, timestamp))
            db.commit()
            return response
            followUp = await awaitMsg(message)

        except websockets.exceptions.ConnectionClosedError as e:
            print(f"Connection closed: {e}")

        except Exception as e:
            print(f"Error: {e}")            

async def awaitMsg(ws):
    message = await ws.recv() 
    print(f'Received message: {message}')
    timestamp = datetime.datetime.now().isoformat()
    sender = 'client'
    db = sqlite3.connect('chat-hub.db')
    db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
               (sender, message, timestamp))
    db.commit()
    try:            
        response = await main(cl.Message(content=message))
        serverResponse = "server response: " + response
        print(serverResponse)
        # Append the server response to the server_responses list
        await ws.send(serverResponse)
        serverSender = 'server'
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                       (serverSender, serverResponse, timestamp))
        db.commit()
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
            output_message = await main(cl.Message(content=input_message))
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

@cl.on_message
async def main(message: cl.Message):
    chain = cl.user_session.get("chain")  # type: ConversationalRetrievalChain
    cb = cl.AsyncLangchainCallbackHandler()

    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    return json.dumps(answer)
    await cl.Message(content=answer, elements=text_elements).send()
