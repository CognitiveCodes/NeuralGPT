import re
import os
import datetime
import sqlite3
import websockets
import json
import asyncio
import time
import queue
import threading
import conteneiro
import pdfplumber
import streamlit as st
import fireworks.client
import PySimpleGUI as sg
import chromadb.utils.embedding_functions as embedding_functions
from tempfile import TemporaryDirectory
from langchain_core.embeddings import Embeddings
from chromadb.api.types import EmbeddingFunction
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from io import BytesIO
from fireworks.client import Fireworks, AsyncFireworks
from langchain_anthropic import ChatAnthropic
from handleMsg import MsgHandler
from agents_neural import Fireworks, Copilot, ChatGPT, Claude3, ForefrontAI, Flowise, Chaindesk, CharacterAI
from operator import itemgetter
from AgentGPT import AgentsGPT
from forefront import ForefrontClient
from PyCharacterAI import Client
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain import hub
from langchain_experimental.tools import PythonREPLTool
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.utilities import GoogleSearchAPIWrapper
from langchain_core.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain_community.vectorstores import Chroma
from langchain.llms.fireworks import Fireworks
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain.llms import HuggingFacePipeline
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_community.document_loaders import TextLoader
from langchain.llms import HuggingFaceHub
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from pathlib import Path
import chromadb

servers = []
clients = []
inputs = []
outputs = []
messagess = []
intentios = []
used_ports = []
server_ports = []
client_ports = []    

class Document:
    def __init__(self, text, metadata=None):
        self.page_content = text if text is not None else ""
        self.metadata = metadata if metadata is not None else {}

class PyPDFLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        documents = []
        with pdfplumber.open(self.file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                documents.append(Document(text))
        return documents
       
class ChromaEmbeddingsAdapter(Embeddings):
    def __init__(self, ef: EmbeddingFunction):
        self.ef = ef

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, query):
        return self.ef([query])[0]

class NeuralAgent:

    def __init__(self):

        working_directory = "D:/streamlit"
        self.system_instruction = f"You are now integrated with a local websocket server in a project of hierarchical cooperative multi-agent framework called NeuralGPT. Your main job is to coordinate simultaneous work of multiple LLMs connected to you as clients. Each LLM has a model (API) specific ID to help you recognize different clients in a continuous chat thread (template: <NAME>-agent and/or <NAME>-client). Your chat memory module is integrated with a local SQL database with chat history. Your primary objective is to maintain the logical and chronological order while answering incoming messages and to send your answers to the correct clients to maintain synchronization of the question->answer logic. However, please note that you may choose to ignore or not respond to repeating inputs from specific clients as needed to prevent unnecessary traffic. As the node of highest hierarchy in the network, you're equipped with additional tools which you can activate by giving a response starting with: 1. '/w' to not respond with anything and keep the client 'on hold'. 2. '/d' to disconnect client from a server. 3. '/s' to perform internet search for subjects provided in your response (e.g. '/s news AI' to search for recent news about AI). 4. '/ws' to start a websocket server on port given by you in response as a number between 1000 and 9999 with the exception of ports that are used already by other servers: {print(conteneiro.servers)}). 5. '/wc' followed by a number between 1000 and 9999 to connect yourself to active websocket servers: {print(conteneiro.servers)}."
 
        self.messages = []
        self.servers = {}
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.past_user_inputs = []
        self.generated_responses = []

        self.clientdb = chromadb.PersistentClient(path=os.path.join(working_directory, "chroma_store"))

        self.server = None              

        c1, c2 = st.columns(2)

        with c1:
            self.srv_con = st.empty()
            self.srv_stat = st.empty()
            self.srv_state = self.srv_stat.status(label="Incoming message", state="complete", expanded=False)

        with c2:
            self.cli_con = st.empty()
            self.cli_stat = st.empty()
            self.cli_state = self.cli_stat.status(label="Server response", state="complete", expanded=False)

        with st.sidebar:
            self.cont = st.empty()        
            self.status = self.cont.status(label="Server info", state="complete", expanded=False)
            self.status.write(self.servers)

    def handleMsg(self):
        self.past_user_inputs.clear()
        self.generated_responses.clear()    
        self.cli_con = st.empty()
        self.srv_con = st.empty()
        self.srv_container = self.srv_con.container(border=True)
        self.cli_container = self.cli_con.container(border=True)

        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 12")
        messages = cursor.fetchall()
        messages.reverse()

        # Collect messages based on sender
        for message in messages:
            if message[1] == 'server':
                self.generated_responses.append(message[2])
            else:
                self.past_user_inputs.append(message[2])

        self.srv_state.write(self.generated_responses)
        self.cli_state.write(self.past_user_inputs)

    def incomingMsg(self, message):
        self.cli_stat = st.empty()
        self.cli_state = self.cli_stat.status(label="Incoming message", state="running", expanded=True)
        self.cli_state.write(message)

    def responseMsg(self, message):
        self.srv_stat = st.empty()
        self.srv_state = self.srv_stat.status(label="Server Response", state="running", expanded=True)
        self.srv_state.write(message)

    
    def run_forever(self):
        asyncio.get_event_loop().run_until_complete(self.start_server())
        asyncio.get_event_loop().run_forever()

    def UIforever(self):
        asyncio.get_event_loop().run_until_complete(self.start_server())
        asyncio.get_event_loop().run_forever()

    async def stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped.")

    def run(self, port):
        self.srv_name = f"Llama3 server port: {port}"
        asyncio.run(self.start_server(port))

    def runUI(self):
        self.thread = threading.Thread(target=self.updateUI)
        # Start the thread
        self.thread.start()

    def getCollection(self, collection_name):
        self.collection = self.clientdb.get_or_create_collection(name=collection_name)
        return self.collection
    
    def add_documents(self, collection, documents):
        self.collection = collection
        for index, document in enumerate(documents):
            self.collection.add(
                documents=[document],
                ids=[f"id{index + 1}"] 
            )

    def save_vector_store(self, window):
        filename = window['-STORE-'].get()  # Use the same key as for API keys or a different one if necessary
        try:
            self.vectordb.save(filename)
            sg.popup('Vector store saved successfully!')
        except Exception as e:
            sg.popup(f"Failed to save vector store: {e}")
        
    def load_vector_store(self, window):
        filename = window['-STORE-'].get()
        try:
            self.vectordb = Chroma.load(filename)
            sg.popup('Vector store loaded successfully!')
            return self.vectordb
        except Exception as e:
            sg.popup(f"Failed to load vector store: {e}")
            return None

    def get_msg_history(self, number, order):
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        exec = f"SELECT * FROM messages ORDER BY timestamp {order} LIMIT {number}"
        cursor.execute(exec)
        msgs = cursor.fetchall()
        return msgs
    
    def get_message_history(self, window, include_timestamp):
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        order = window['-ORDER-'].get()
        number = window['-MSGNUMBER-'].get()
        if include_timestamp:
            query = f"SELECT message, timestamp FROM messages ORDER BY timestamp {order} LIMIT {number}"
        else:
            query = f"SELECT message FROM messages ORDER BY timestamp {order} LIMIT {number}"
        cursor.execute(query)
        if include_timestamp:
            msgs = [{'message': row[0], 'timestamp': row[1]} for row in cursor.fetchall()]
        else:
            msgs = [row[0] for row in cursor.fetchall()]
        return msgs

    def createVectordb(self, splits, collection_name):
        self.vectorPDF = self.create_db(splits, collection_name)
        return self.vectorPDF

    def splitPDF(self, documents, window):
        size = int(window['-CHUNK-'].get())
        overlap = int(window['-OVERLAP-'].get())
        doc_texts = [doc.page_content for doc in documents]  # Ensure you're working with text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(doc_texts)
        return doc_splits

    def process_PDFdocuments(self, documents, window):
        size = int(window['-CHUNK-'].get())
        overlap = int(window['-OVERLAP-'].get())
        doc_texts = [doc.page_content for doc in documents]  # Ensure you're working with text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(doc_texts)
        return doc_splits

    def process_TXTdocuments(self, documents, window):
        size = int(window['-CHUNK-'].get())
        overlap = int(window['-OVERLAP-'].get())
        doc_texts = [doc.page_content for doc in documents]  # Ensure you're working with text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(doc_texts)
        return doc_splits

    # Function to process documents or chat history and create vector database
    def process_documents(self, documents, collection_name, size, overlap):
        # If documents include timestamps, extract just the messages
        if isinstance(documents[0], dict):
            documents = [doc['message'] for doc in documents if doc['message'] is not None]
        # Wrap documents in the Document class, ensuring no None values for page_content
        doc_objects = [Document(doc) for doc in documents if doc is not None]
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=size, 
            chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(doc_objects)
        self.vectordb = self.create_db(doc_splits, collection_name)
        return self.vectordb

    def splitDocuments(self, documents, size, overlap):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=size, 
            chunk_overlap=overlap)
        splits = text_splitter.split_documents(documents)
        return splits

    def createPDFstore(self, splits, collection_name):
        self.vectordb = self.create_db(splits, collection_name)
        return self.vectordb

    def process_pdf(self, file_path, chunk, overlap):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        print(f"Loaded documents: {documents}")  # Debug: Check what's loaded

        if documents and isinstance(documents[0], Document):
            processed_content = [doc.page_content for doc in documents]
        else:
            print(f"Error: Documents are not of type Document, they are {type(documents[0])}")  # Debug: Type check
            raise TypeError("Expected a list of Document objects")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk, chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(processed_content)
        return doc_splits

    # Load PDF document and create doc splits
    def load_pdf(self, file_path, chunk, overlap):
        with pdfplumber.open(file_path) as pdf:
            all_text = [page.extract_text() for page in pdf.pages if page.extract_text()]
        
        if not all_text:
            print(f"No text found in the entire document: {file_path}")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk, 
            chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(all_text)
        return doc_splits

    def PDFload(self, list_file_path, chunk_size, chunk_overlap):
        # Processing for one document only
        # loader = PyPDFLoader(file_path)
        # pages = loader.load()
        loaders = [PyPDFLoader(x) for x in list_file_path]
        pages = []
        for loader in loaders:
            pages.extend(loader.load())
        # text_splitter = RecursiveCharacterTextSplitter(chunk_size = 600, chunk_overlap = 50)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size, 
            chunk_overlap = chunk_overlap)
        doc_splits = text_splitter.split_documents(pages)
        return doc_splits

    def process_txt(self, file_paths, chunk, overlap):
        contents = []  # Initialize a list to hold the contents of all files
        for file_path in file_paths:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                contents.append(content)  # Append each file's content to the list
        # Split the combined content
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk, chunk_overlap=overlap)
        doc_splits = text_splitter.split_documents(contents)  # Ensure it's a list
        return doc_splits

    def process_docs(self, documents):
        txt_documents = []
        pdf_documents = []

        for file_path in documents:
            if file_path.endswith('.txt'):
                txt_documents.append(file_path)
            elif file_path.endswith('.pdf'):
                pdf_documents.append(file_path)

        # Extract text from TXT files
        extracted_txt = []
        for txt_file in txt_documents:
            with open(txt_file, 'r', encoding='utf-8') as file:
                extracted_txt.append(file.read())

        # Extract text from PDF files
        extracted_pdf = []
        for pdf_file in pdf_documents:
            with pdfplumber.open(pdf_file) as pdf:
                text = ''
                for page in pdf.pages:
                    text += page.extract_text() + '\n'
                extracted_pdf.append(text)

        # Combine extracted text for upload
        all_extracted_text = extracted_txt + extracted_pdf
        return all_extracted_text

    def getRetriever(self, text, name):
        self.vectorstore = Chroma.from_texts(
            texts=text,
            collection_name=name,
            embedding=ChromaEmbeddingsAdapter(SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")),
        )        
        return self.vectorstore

    def documents_process(self, file_path, window):
        if file_path.endswith('.pdf'):
            documents = self.process_pdf(file_path)
        elif file_path.endswith('.txt'):
            documents = self.process_txt(file_path)
        else:
            sg.popup("Unsupported file type")
            return None

        # Assuming process_documents returns a list of processed documents
        collection_name = 'document_vectors'
        self.vector_store = self.process_documents(documents, collection_name, window)
        return self.vector_store

    # Example usage within the class
    def use_message_history(self, include_timestamp=True):
        messages = self.get_message_history(100, 'DESC', include_timestamp)
        collection_name = 'chat_history'
        vector_db = self.process_documents(messages, 600, 50, collection_name)
        return vector_db
    
    def getCollection(self, name):
        collection = self.clientdb.get_collection(name=name)
        return collection
    
    def deleteCollection(self, name):
        collection = self.clientdb.create_collection(name=name)
        return collection
    
    def createCollection(self, name):
        collection = self.clientdb.create_collection(name=name)
        return collection

    def get_collections(self):
        collection_names = self.clientdb.list_collections()
        return collection_names
    
    def get_collection_ids(self, collection_name):
        collection = self.clientdb.get_collection(collection_name)
        ids = collection.get_ids()  # Assuming this method exists to get IDs
        return ids    

    def get_existing_documents(self, collection_name):
        collection = self.clientdb.get_collection(collection_name)
        documents = collection.get(include=["documents"])
        return documents

    def load_and_process_documents(self, window):
        file_path = window['-DOCFILE-'].get()
        chunk = window['-CHUNK1-'].get()
        overlap = window['-OVERLAP1-'].get
        if file_path.endswith('.pdf'):
            self.documents = self.process_pdf(file_path, chunk, overlap)                
        else:                
            self.documents = self.process_txt(file_path, chunk, overlap)
        return self.documents

    def load_doc(list_file_path, chunk_size, chunk_overlap):
        loaders = [PyPDFLoader(x) for x in list_file_path]
        pages = []
        for loader in loaders:
            # Assuming each loader returns a list of Document objects with file paths
            for document in loader.load():
                if isinstance(document.page_content, str) and os.path.isfile(document.page_content):
                    with open(document.page_content, 'rb') as file:
                        pdf = pdfplumber.open(file)
                        text = ''
                        for page in pdf.pages:
                            text += page.extract_text() + '\n'
                        pages.append(Document(text))
                elif isinstance(document.page_content, bytes):
                    with pdfplumber.open(BytesIO(document.page_content)) as pdf:
                        text = ''
                        for page in pdf.pages:
                            text += page.extract_text() + '\n'
                        pages.append(Document(text))
                else:
                    raise ValueError("Document.page_content must be a file path or PDF bytes")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size, 
            chunk_overlap = chunk_overlap)
        doc_splits = text_splitter.split_documents([page.page_content for page in pages])
        return doc_splits

    async def querydb(self, query_txt, query_type):
        results = self.vectordb.search(query_txt, query_type)
        name = "Query result"
        result = str(results)
        data = json.dumps({"name": name, "message": result})
        return data
    
    def get_documents_from_collection(self, collection_name):
        # Get the collection from the persistent client
        collection = self.clientdb.get_collection(collection_name)
        
        # Retrieve documents from the collection
        documents = collection.get(include=["documents"])
        # Format documents into a list of Document objects
        formatted_documents = [Document(doc['content'], metadata=doc.get('metadata')) for doc in documents]
        
        return documents
        
    def create_langchain_db(self, api_keys, collection_name):
        api_cohere = api_keys.get('CohereAPI', '')
        api_fireworks = api_keys.get('APIfireworks', '')
        embedding = CohereEmbeddings(cohere_api_key=api_cohere)
        self.langchain_chroma = Chroma(
            client=self.clientdb,
            collection_name=collection_name,
            embedding_function=embedding,
        )

        return self.langchain_chroma

    # Create vector database
    def create_db(self, splits, collection_name):
        embedding = HuggingFaceEmbeddings()

        # Create or get the collection from the persistent client
        collection = self.clientdb.get_or_create_collection(collection_name)

        # Create the Chroma vector store using the provided splits and embedding
        vectordb = Chroma.from_documents(
            documents=splits,
            embedding=embedding,
            client=self.clientdb,
            collection_name=collection_name,
            persist_directory="./chroma_db"
        )
        
        # Persist the vector store
        vectordb.persist()
        return vectordb


    # Load vector database
    def load_db(self):
        embedding = HuggingFaceEmbeddings()
        vectordb = Chroma(
            persist_directory="./chroma_db", 
            embedding_function=embedding)
        return vectordb

    # Define a function that will run the client in a separate thread
    def runn(self):
        def start_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.updateUI())
            loop.run_forever()

        UIthread = threading.Thread(target=start_loop)
        UIthread.daemon = True  # Optional: makes the thread exit when the main program exits
        UIthread.start()

    async def stop_specific_server(self, port):
        for server in servers.values():
            if server['port'] == port:
                await self.stop_server(server['server'])
                break

    # Define a function that will run the client using asyncio         
    async def stop_server(self, server):
        if self.server:    
            # Close all client connections
            for client in servers[server]['clients']:
                await client.close(reason='Server shutdown')
            # Stop the server
            conteneiro.servers.remove(self.srv_name)
            self.servers.remove(self.srv_name)
            conteneiro.clients.clear() 
            self.clients.clear()            
            await server.close()
            await server.wait_closed()
            print(f"WebSocket server on port {servers[server]['port']} stopped.")

    def ask_interpreter(self, instruction, question, provider, api_keys):
          
        os.environ["FIREWORKS_API_KEY"] = api_keys.get('APIfireworks', '')
        os.environ["ANTHROPIC_API_KEY"] = api_keys.get('APIanthropic', '')

        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.5, max_tokens=3200, timeout=None, max_retries=2)

        tools = [PythonREPLTool()]
        
        base_prompt = hub.pull("langchain-ai/react-agent-template")
        prompt = base_prompt.partial(instructions=instruction)

        app = create_react_agent(llm, tools, messages_modifier=instruction)
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools)

        messages = app.invoke({"messages": [("user", question)]})
        ai_message = messages['messages'][-1].content
        name = "Langchain file system agent"
        res = json.dumps({"name": name, "message": ai_message})
        return res

        return mes

    def get_search(self, question, provider, api_keys):
          
        os.environ["GOOGLE_CSE_ID"] = api_keys.get('GoogleCSE', '')
        os.environ["GOOGLE_API_KEY"] = api_keys.get('GoogleAPI', '')

        search = DuckDuckGoSearchResults()

        tool = Tool(
            name="google_search",
            description="Search Google for recent results.",
            func=search.run,
        )

        search_results = search.run(question, 5)

        return search_results

    def list_dir(self, dir_path):
 
        tools = FileManagementToolkit(
            root_dir=str(dir_path),
            selected_tools=[
                "list_directory"
            ],
        ).get_tools()
 
        list_tool = tools[0]  # Get the first tool, which should be the list_directory tool
        dir_list = list_tool.invoke({})  # Invoke the tool with an empty dictionary
        return dir_list

    def file_read(self, dir_path, file):
 
        tools = FileManagementToolkit(
            root_dir=str(dir_path),
            selected_tools=[
                "read_file"
            ],
        ).get_tools()
 
        read_tool = tools[0]
        file_cont = read_tool.invoke({"file_path": file}) 
        return file_cont
    
    def file_write(self, dir_path, file, content):
 
        tools = FileManagementToolkit(
            root_dir=str(dir_path),
            selected_tools=[
                "write_file"
            ],
        ).get_tools()
 
        write_tool = tools[0]
        write_tool.invoke({"file_path": file, "text": content}) 
        return "File written successfully!"

    async def file_agent(self, question, provider, api_keys):
        working_directory = TemporaryDirectory()  

        tools = FileManagementToolkit(
            root_dir=str(working_directory.name),
            selected_tools=[
                "copy_file",
                "delete_file",
                "move_file",
                "read_file", 
                "write_file", 
                "list_directory"
                ],
        ).get_tools()

        copy_tool, delete_tool, move_tool, read_tool, write_tool, list_tool = tools
        return 

    def ask_file_agent1(self, dir_path, question, provider, api_keys):
          
        os.environ["FIREWORKS_API_KEY"] = api_keys.get('APIfireworks', '')
        os.environ["ANTHROPIC_API_KEY"] = api_keys.get('APIanthropic', '')

        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.5, max_tokens=3200, timeout=None, max_retries=2)

        tools = FileManagementToolkit(
            root_dir=str(dir_path)
        ).get_tools()
        
        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            max_iterations=3,
            return_intermediate_steps=True
        )

        results = agent.invoke(question)
        print(results)
        ai_message = results['messages'][-1].content
        name = "Langchain internet-search agent"
        res = json.dumps({"name": name, "message": ai_message})
        return res
    
    def get_search_agent(self, question, provider, api_keys):
          
        os.environ["GOOGLE_CSE_ID"] = api_keys.get('GoogleCSE', '')
        os.environ["GOOGLE_API_KEY"] = api_keys.get('GoogleAPI', '')
        os.environ["FIREWORKS_API_KEY"] = api_keys.get('APIfireworks', '')
        os.environ["ANTHROPIC_API_KEY"] = api_keys.get('APIanthropic', '')
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_keys.get('HuggingFaceAPI', '')

        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.5, max_tokens=3200, timeout=None, max_retries=2)

        search = DuckDuckGoSearchResults()
        system_message = "You are an agent working as an instance of hierarchical cooperative multi-agent framework called NeuralGPT. You are responsible for handling operations on a local file system."

        tools = load_tools(["google-search"], llm=llm)
        tool = Tool(
            name="google_search",
            description="Search Google for recent results.",
            func=search.run,
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an agent working as an instance of hierarchical cooperative multi-agent framework called NeuralGPT. You are responsible for operations associated with gathering data from internet and providing it to other instances."),
                ("human", "{input}"),
                # Placeholders fill up a **list** of messages
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        app = create_react_agent(llm, tools, messages_modifier=system_message)

        results = app.invoke({"messages": [("user", question)]})
        print(results)
        ai_message = results['messages'][-1].content
        name = "Langchain internet-search agent"
        res = json.dumps({"name": name, "message": ai_message})
        return res

    def ask_file_agent(self, dir_path, question, provider, api_keys):
        os.environ["GOOGLE_CSE_ID"] = api_keys.get('GoogleCSE', '')
        os.environ["GOOGLE_API_KEY"] = api_keys.get('GoogleAPI', '')
        os.environ["FIREWORKS_API_KEY"] = api_keys.get('APIfireworks', '')
        os.environ["ANTHROPIC_API_KEY"] = api_keys.get('APIanthropic', '')
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_keys.get('HuggingFaceAPI', '')


        llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.5, max_tokens=3200, timeout=None, max_retries=2)

        system_message = "You are an agent working as an instance of hierarchical cooperative multi-agent framework called NeuralGPT. You are responsible for handling operations on a local file system."

        tools = FileManagementToolkit(
            root_dir=str(dir_path)
        ).get_tools()

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are an agent working as an instance of hierarchical cooperative multi-agent framework called NeuralGPT. You are responsible for handling operations on a local file system."),
                ("human", "{input}"),
                # Placeholders fill up a **list** of messages
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        app = create_react_agent(llm, tools, messages_modifier=system_message)
        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools)

        messages = app.invoke({"messages": [("user", question)]})
        ai_message = messages['messages'][-1].content
        name = "Langchain file system agent"
        res = json.dumps({"name": name, "message": ai_message})
        return res

    def initialize_llmchain(self, provider, api_keys, docs, name):
        os.environ["GOOGLE_CSE_ID"] = api_keys.get('GoogleCSE', '')
        os.environ["GOOGLE_API_KEY"] = api_keys.get('GoogleAPI', '')
        os.environ["FIREWORKS_API_KEY"] = api_keys.get('APIfireworks', '')
        os.environ["ANTHROPIC_API_KEY"] = api_keys.get('APIanthropic', '')
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = api_keys.get('HuggingFaceAPI', '')

        self.vectorstore = Chroma.from_texts(
            texts=docs,
            collection_name=name,
            embedding=ChromaEmbeddingsAdapter(SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")),
        )
        if provider == "Fireworks":
            llm = Fireworks(model="accounts/fireworks/models/llama-v3-8b-instruct", model_kwargs={"temperature":0.5, "max_tokens":4000, "top_p":1.0})
        if provider == "Claude3":
            llm = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.5, max_tokens=3200, timeout=None, max_retries=2)
        
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            output_key='answer',
            return_messages=True
        )

        # Use the langchain_chroma as the retriever
        self.retriever = self.vectorstore.as_retriever()
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=self.retriever,
            chain_type="stuff", 
            memory=memory,
            return_source_documents=True,
            verbose=False,
        )
        combine_docs_chain = create_stuff_documents_chain(
            llm, retrieval_qa_chat_prompt
        )
        retrieval_chain = create_retrieval_chain(self.retriever, combine_docs_chain)
        return self.qa_chain

    def format_chat_history(self, chat_history):
        formatted_chat_history = []
        for user_message, bot_message in chat_history:
            formatted_chat_history.append(f"User: {user_message}")
            formatted_chat_history.append(f"Assistant: {bot_message}")
        return formatted_chat_history
        

    def ask(self, instruction, question, something):
        history = []
        past_user_inputs = []
        generated_responses = []
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 8")
        messages = cursor.fetchall()
        messages.reverse()                                    

        # Collect messages based on sender
        for message in messages:
            if message[1] == 'server':
                generated_responses.append(message[2])
            else:
                past_user_inputs.append(message[2])

        history.append(f"System: {str(instruction)}")

        min_length = min(len(past_user_inputs), len(generated_responses))

        for i in range(min_length):
            history.append(f"User: {str(past_user_inputs[i])}")
            history.append(f"Assistant: {str(generated_responses[i])}")
   
        try:
            # Generate response using QA chain
            response = self.qa_chain({"question": question, "chat_history": history})
            answer = response["answer"]
            sources = response["source_documents"]
            source1 = sources[0].page_content.strip()
            source2 = sources[1].page_content.strip()
            # Langchain sources are zero-based
            name = "Langchain agent server"
            resp = f"{answer} - sources: {source1, source2}"
            data = json.dumps({"name": name, "message": resp})
            return (data)
        
        except Exception as e:
            print(f"Error: {e}")    
        
    def ask2(self, instruction, question, tokens):
        history = []
        past_user_inputs = []
        generated_responses = []
        db = sqlite3.connect('chat-hub.db')
        cursor = db.cursor()
        cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 8")
        messages = cursor.fetchall()
        messages.reverse()                                    

        # Collect messages based on sender
        for message in messages:
            if message[1] == 'client':
                generated_responses.append(message[2])
            else:
                past_user_inputs.append(message[2])

        history.append(f"System: {str(instruction)}")

        # Ensure the history list has alternating user and assistant messages       
        min_length = min(len(past_user_inputs), len(generated_responses))

        for i in range(min_length):
            history.append(f"User: {str(past_user_inputs[i])}")
            history.append(f"Assistant: {str(generated_responses[i])}")
   
        try:
            # Generate response using QA chain
            response = self.qa_chain({"question": question, "chat_history": history})
            answer = response["answer"]
            sources = response["source_documents"]
            source1 = sources[0].page_content.strip()
            source2 = sources[1].page_content.strip()
            name = "Langchain agent client"
            resp = f"{answer} - sources: {source1, source2}"
            data = json.dumps({"name": name, "message": resp})
            return (data)
        
        except Exception as e:
            print(f"Error: {e}") 

    # Initialize database
    def initialize_database(self, list_file_obj, chunk_size, chunk_overlap):
        # Create list of documents (when valid)
        list_file_path = [x.name for x in list_file_obj if x is not None]
        collection_name = Path(list_file_path[0]).stem
        # Fix potential issues from naming convention
        collection_name = collection_name.replace(" ","-") 
        collection_name = collection_name[:50]
        # print('list_file_path: ', list_file_path)
        print('Collection name: ', collection_name)
        # Load document and create splits
        doc_splits = self.load_doc(list_file_path, chunk_size, chunk_overlap)
        # global vector_db
        vector_db = self.create_db(doc_splits, collection_name)
        return vector_db, collection_name, "Complete!"


    def initialize_LLM(self, vector_db, provider):
        # print("llm_option",llm_option)
        llm_name = provider
        print("llm_name: ",llm_name)
        qa_chain = self.initialize_llmchain(llm_name, 0.5, 3200, 1.0, vector_db)
        return qa_chain, "Complete!"

    async def clientHandler(self, window, neural, message, SQLagent, PDFagent, searchAgent, fileAgent, follow_up):
        sys_msg = f"""You are temporarily working as main autonomous decision-making 'module' responsible for handling server<->clients websocket connectivity. Your main and only job is to decide what action should be taken in response to messages incoming from clients by answering with a proper command-function.
        As a server node of the framework, you have the capability to respond to clients inputs in 3 different ways:
        - with command-function: '/giveAnswer' to send your response to a given client without taking any additional actions.
        - with command-function: '/takeAction' to take additional action that might be required from you by the client.
        - with command-function: '/keepOnHold' to not respond to the client in any way but maintain an open server<->client communication channel.
        It is crucial for you to respond only with one of those 3 command-functions in their exact forms and nothing else, as those phrases are being used to 'trigger' desired functions - that's why the number of tokens iun your response will be limited to 5. 
        """
        msgCli = f""" SYSTEM MESSAGE: This message was generated automatically in response to an input received from a client - this is the messsage in it's orginal form:
        ----
        {message}
        ----
        As a server node of the framework, you have the capability to respond to clients inputs in 3 different ways:
        - with command-function: '/giveAnswer' to send your response to a given client without taking any additional actions.
        - with command-function: '/takeAction' to take additional action that might be required from you by the client.
        - with command-function: '/keepOnHold' to not respond to the client in any way but maintain an open server<->client communication channel.
        It is crucial for you to respond only with one of those 3 command-functions in their exact forms and nothing else, as those phrases are being used to 'trigger' desired functions - that's why the number of tokens iun your response will be limited to 5.
        """
        try:            
            response = await neural.ask(sys_msg, msgCli, 5)

        except Exception as e:
            print(f"Error: {e}")    
                                        


    async def stop_client(self):
        conteneiro.clients.remove(self.cli_name2)        
        # Close the connection with the server
        await self.websocket.close()
        print("Stopping WebSocket client...")

    async def pickServer(self, agent, srvList):
        activeSrv = str(conteneiro.servers)
        instruction = f"This question is part of a function responsible for sending messages to a client chosen by you from those connected to a specific websocket server. Your only job is to respond with a number of port at which the websocket server is running. List of currently active servers to which the desired client is connected is provided here: {srvList} - '[]' means that there are no active servers and the list is empty, so all numbers in range 1000-9999 are available for you to choose. Remember that your response shouldn't include anything except the chosen number in range, as it will be used as argument for another function that accepts only integer inputs."
        command = f"Launch server on a port of your choice"
        response = await agent.askAgent(instruction, inputs, outputs, command, 5)
        print(response)
        data = json.loads(response)
        text = data['message']

    async def pickPortSrv(self, agent, inputs, outputs):
        activeSrv = str(conteneiro.servers)
        instruction = f"This question is part of a function launching websocket servers at ports chosen by you. Your only job is to respond with a number in range from 1000 to 9999 excluding port numbers which are already used by active websocket servers. List of currently active server to which you can be connected is provided here: {activeSrv} - '[]' means that there are no active servers and the list is empty, so all numbers in range 1000-9999 are available for you to choose. Remember that your response shouldn't include anything except the chosen number in range, as it will be used as argument for another function that accepts only integer inputs."
        command = f"Launch server on a port of your choice"
        response = await agent.askAgent(instruction, inputs, outputs, command, 5)
        print(response)
        data = json.loads(response)
        text = data['message']
        match = re.search(r'\d+', text)        
        number = int(match.group())  
        print(f"port chosen by agent: {number}")
        return int(number)

    async def pickPortCli(self, agent, srvrs):
        activeSrv = str(srvrs)
        instruction = f"This question is part of a function connecting you as a client to active websocket servers running at specific ports. Your only job is to respond with a number of a port yo which you want to be connected. List of currently active server to which you can be connected is provided here: {activeSrv} - if the list is empty, then there's no active servers. Remember that your response shouldn't include anything except the number of port to which you want to be connected, as it will be used as argument for another function that accepts only integer inputs." 
        response = await agent.askAgent(instruction, inputs, outputs, activeSrv, 5)
        print(response)
        match = re.search(r'\d+', response)        
        number = int(match.group())
        print(f"port of server chosen by agent: {number}")
        return number

    async def defineMessageToInterpreter(self, inputs, outputs, message, neural):
        instruction = f"You are now temporarily working as a part of agent-to-agent communication system. Your current job is to define questions directed to an agent specializing in working with Python code. Remember to formulate clear instructions associated with the subject(s) discussed in the message that will be given to you as context."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by formulating instruction for a fellow agent specialized in working with Python code. Your instructionsa should involve tasks involving coding in Python associated with the subject(s) discussed in the following message: {message}."
        msg = await neural.askAgent(instruction, inputs, outputs, question, 1500)
        print(msg)
        data = json.loads(msg)
        msgText = data['message']
        return msgText

    async def pickCollection(self, inputs, outputs, neural, collections):
        instruction = f"You are now temporarily working as a part of function allowing to query documents database. Your main and only job is to analyze the input message and respond only (!) with the namme of collection which you'd like to query. Remember that you response needs to consist the collection name only in exactly the same form as provided in the list"
        question = f"Respond only with the collection name chosen from the following list of existingcollections: {collections}."
        collection = await neural.askAgent(instruction, inputs, outputs, question, 150)
        return collection

    async def defineQuery(self, inputs, outputs, message, neural):
        instruction = f"You are now temporarily working as a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by naming the subject which you'd like to search for in the message history. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the message that will be given to you."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by naming the subject which you'd like to search for in the message history. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the following message: {message}."
        query = await neural.askAgent(instruction, inputs, outputs, question, 150)
        return query

    async def defineDocumentQuery(self, inputs, outputs, message, neural, PDFagent):
        collection_list = PDFagent.get_collections()
        query = await self.definePDFQuery(inputs, outputs, message, neural)
        
        instruction = f"You are now temporarily working as a part of function allowing to query document vector store database. Your main and only job is to analyze the input message and respond by naming the subject which you'd like to search for in the provided documents. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the message that will be given to you."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by naming the subject which you'd like to search for in the message history. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the following message: {message}."
        query = await neural.askAgent(instruction, inputs, outputs, question, 150)
        return query

    async def definePDFQuery(self, inputs, outputs, message, neural):
        instruction = f"You are now temporarily working as a part of function allowing to query document vector store database. Your main and only job is to analyze the input message and respond by naming the subject which you'd like to search for in the provided documents. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the message that will be given to you."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by naming the subject which you'd like to search for in the message history. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the following message: {message}."
        query = await neural.askAgent(instruction, inputs, outputs, question, 150)
        return query

    async def messageSQLAgent(self, inputs, outputs, message, neural):
        instruction = f"You are now temporarily working as a part of function allowing to perform multiple actions on chat history database using a Langchain agent. Your main and only job is to analyze the input message and respond by formulating the question/task which the agent should perform. Remember to keep your response as short as possible - respond with single sentence that can be understood by agent and summarizes the subject(s) discussed in the message that will be given to you."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by formulating the question/task whioch the agent should perform. Remember to keep your response as short as possible - respond with single sentence that can be understood by agent and summarizes the subject(s) discussed in the following message: {message}."
        query = await neural.askAgent(instruction, inputs, outputs, question, 150)
        return query
    
    async def messagePDFAgent(self, inputs, outputs, message, neural):
        instruction = f"You are now temporarily working as a part of function allowing to perform multiple actions on document vector store using a Langchain agent. Your main and only job is to analyze the input message and respond by formulating the question/task which the agent should perform. Remember to keep your response as short as possible - respond with single sentence that can be understood by agent and summarizes the subject(s) discussed in the message that will be given to you."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by formulating the question/task whioch the agent should perform. Remember to keep your response as short as possible - respond with single sentence that can be understood by agent and summarizes the subject(s) discussed in the following message: {message}."
        query = await neural.askAgent(instruction, inputs, outputs, question, 1500)
        return query

    async def defineFileAgentInput(self, inputs, outputs, message, neural):
        instruction = f"You are now temporarily working as a part of function allowing to perform multiple actions on document vector store using a Langchain agent. Your main and only job is to analyze the input message and respond by formulating the question/task which the agent should perform. Remember to keep your response as short as possible - respond with single sentence that can be understood by agent and summarizes the subject(s) discussed in the message that will be given to you."
        question = f"This input is a part of function allowing to query chat history database. Your main and only job is to analyze the input message and respond by formulating the question/task whioch the agent should perform. Remember to keep your response as short as possible - respond with single sentence that can be understood by agent and summarizes the subject(s) discussed in the following message: {message}."
        task = await neural.askAgent(instruction, inputs, outputs, question, 500)
        return task

    async def pickFile(self, inputs, outputs, neural, file_list):
        instruction = f"You are now temporarily working as a part of function allowing to perform operations on a local file system. Your main and only job is to analyze the past message exchange and respond respond with only (!) the name of a file which contents you'd like to read or modify."
        question = f"This is the list of all files available curenly in the working directory: {file_list}. Remember that it is crucial for you to iinclude the file format (extension) in your response, otherwise you won't be able to read the contents of that file."
        query = await neural.askAgent(instruction, inputs, outputs, question, 500)
        return query   

    async def pickSearch(self, inputs, outputs, question, neural):
        instruction = f"This input is a part of function allowing agents to browse internet. Your main and only job is to analyze the input message and respond by naming the subject(s) to use while performing internet search. Remember to keep your response as short as possible - respond with single words and/or short sentences that summarize the subject(s) discussed in the message that will be given to you."
        response = await neural.askAgent(instruction, inputs, outputs, question, 150)
        print(response)
        return str(response)
    
    async def getMessageToClient(self, neural, inputs, outputs, msg):
        instruction = f"You are now temporarily working as a part of function allowing to send messages directly to a chosen client connected to you (server). Your main job will be to: first, prepare the message that will be sent and then to pick the desired client's name from a list of clients that will be provided to you."
        cliMsg1 = f"""This is an automatic message generated because you've decided to send a message to a chosen client in response to received input: 
        -----
        {msg}
        -----
        Your current job, is to prepare the message that will be later sent to a client chosen by you in next step of the sending process. Please respond to this message just as you want it to be sent
        """        
        response = await neural.ask(instruction, cliMsg1, 2500)
        print(response)
        inputs.append(cliMsg1)
        outputs.append(response)
        return str(response)

    async def chooseClient(self, neural, list, inputs, outputs, msg):
        instruction = f"TYou are now temporarily working as a part of function allowing to send messages directly to a chosen client connected to you (server). Your main job will be to: first, prepare the message that will be sent and then to pick the desired client's name from a list of clients that will be provided to you."
        cliMsg2 = f"""This is an automatic message generated because you've decided to send a message to a chosen client and already prepared the message to sent which you can see here:
        -----
        {msg}
        -----
        Your current job is to choose the client to which this message should be sent.To do it, you need to answer with the name chosen from following list of clients connected to you:
        -----
        {list}
        Renember that your response can't include anything besides the client's name, otherwise the function won't work.
        """
        response = await neural.askAgent(instruction, inputs, outputs, cliMsg2, 5)
        print(response)
        inputs.append(cliMsg2)
        outputs.append(response)
        return response

    async def google_search(self, question):

        subject = await self.pickSearch(question)
        agent = AgentsGPT()
        results = await agent.get_response(subject)
        result = f"AgentsGPT internet search results: {results}"                
        output_Msg = st.chat_message("ai")
        output_Msg.markdown(result)
        return result
    
    async def launchServer(self, agent):
        serverPort = await self.pickPortSrv(agent)
        await self.start_server_thread(serverPort)

    async def connectClient(self, agent):
        clientPort = await self.pickPortCli(agent)
        await self.startClient(clientPort)

    async def ask_chaindesk(self, agentID, question):
        id = "clhet2nit0000eaq63tf25789"
        agent = Chaindesk(agentID)
        response = await agent.handleInput(question)
        print(response)
        return response

    async def pickCharacter(self, agent, question):
        characterList = f"List of available characters:/d 1. Elly/d 2. NeuralAI" 
        instruction = f"This is a function allowing agents to choose a specific character from a list of characters deployed on Character.ai platform. Your only job is to choose which character you want to speak with using the input message as a context and respond with the name of chosen character. You don't need to say anything Except the name of character from the followinng list: {characterList}."
        inputo = f"Use the following question as context for you to choose which character from Character.ai platform you want to speak with./dQuestion for context: {question}/d List of chharacters for you to choose: {characterList}/d Respond with the name of chosen character to establish a connection."
        character = await agent.ask(instruction, inputo, 50)
        print(character)

        if re.search(r'Elly', character):
            characterID = f"WnIwl_sZyXb_5iCAKJgUk_SuzkeyDqnMGi4ucnaWY3Q"
            return characterID

        if re.search(r'NeuralAI', character):
            characterID = f"_1xlg0qQZl39ds3dbkXS8iWckZGNTRrdtdl0_sjvdJw"
            return characterID 

        else:
            response = f"You didn't choose any character to establish a connection with. Do you want try once again or maybe use some other copmmand-fuunction?"   
            print(response)
            await self.handleInput(response)

    async def decide(self, neural, msg):
        instruction = f"You are temporarily working as a part of decision-making system in a multi-agent framework. Your one and only work, is to analyze the imput message and decide, what should be the next action you will take. You will have only two options to choose: to return the input message using a command '/returnMessage', so it will be sent back to websovket server/client or displayed for the user or to take another action (perform another follow-up) using a command '/followUp'. Your output is limiteed to 5 tokens, so answer only with one of those two commands and nothing else."
        question = f"This message was generated automatically as a part of decision-makingg system utilized by NeuralGPT project, as a follow-up to your last response, which together with the previous input is provided here as context - {msg} Remember that your answer has to include just the command chosen by you and nothing else: '/returnMessage' to use the provided message as response iin conversation or '/followUp' to initialize another follow-up loop."
        answer = await neural.ask(instruction, question, 5)
        print(answer)
        return answer

    async def askCharacter(self, characterAI):
        characterID = await self.pickCharacter()
        msg = "You are about to connect to a Character.ai platform. Please formulate your message in a way that would be understandable for a Character.ai chatbot picked by you."
        res = self.chatFireworks(self.system_instruction, msg, 1500)
        character = CharacterAI(characterAI, characterID)
        answer = await character.handleInput(res)
        return answer    

    async def ask_Claude(self, question):
        claude = Claude3(self.anthropicAPI)
        response = await claude.handleUser(self.system_instruction, question)
        print(response)
        return response    

    async def handleInput(self, question): 

        print(f"Incoming message : {question}")
        timestamp = datetime.datetime.now().isoformat()
        sender = 'client'
        db = sqlite3.connect('chat-hub.db')
        db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                    (sender, question, timestamp))
        db.commit()
        if question.startswith('/s'):        
            agent = AgentsGPT()
            results = await agent.get_response(question)
            result = f"AgentsGPT internet search results: {results}"
            print(result)
            output_Msg = st.chat_message("ai")
            output_Msg.markdown(result)
            answer = await self.chatFireworks(result)
            print(answer)
            output_Msg.markdown(answer)
            return result        
        else:            
            try:
                instruction = """...
                """
                response = await self.chatFireworks(instruction, question)
                answer = f"Fireworks Llama2 agent: {response}"
                serverSender = 'server'
                timestamp = datetime.datetime.now().isoformat()
                db = sqlite3.connect('chat-hub.db')
                db.execute('INSERT INTO messages (sender, message, timestamp) VALUES (?, ?, ?)',
                            (serverSender, response, timestamp))
                db.commit()

                if re.search(r'/search', response):
                    search = await self.google_search(response)
                    answer1 = await self.chatFireworks(instruction, search)
                    output = f"Llama2 agent response: {answer1}"
                    outputMsg = st.chat_message("ai")
                    outputMsg.markdown(output)
                    return output

                if re.search(r'/silence', response):
                    print("...<no response>...")
                    output_Msg = st.chat_message("ai")
                    output_Msg.markdown("...<no response>...")                
                    return
                
                if re.search(r'/disconnect', response):
                    await self.stop_client()
                    res = "successfully disconnected"
                    return res

                if re.search(r'/start_server', response):
                    await self.launchServer()
                   
                if re.search(r'/connect_client', response):
                    await self.connectClient()

                else:
                    return answer

            except Exception as e:
                print(f"Error: {e}")    

class MsgHandler:       

    def __init__(self):

        self.messages = []
        self.servers = []
        self.clients = []
        self.inputs = []
        self.outputs = []
        self.used_ports = []
        self.server_ports = []
        self.client_ports = []
        self.past_user_inputs = []
        self.generated_responses = []
        self.server = None    

        self.server = None              

        c1, c2 = st.columns(2)

        with c1:
            self.srv_con = st.empty()
            self.srv_stat = st.empty()
            self.srv_state = self.srv_stat.status(label="Llama3", state="complete", expanded=False)

        with c2:
            self.cli_con = st.empty()
            self.cli_stat = st.empty()
            self.cli_state = self.cli_stat.status(label="Llama3", state="complete", expanded=False)

        with st.sidebar:
            self.cont = st.empty()        
            self.status = self.cont.status(label="Incoming message", state="complete", expanded=False)

    async def clientHandler(self, message):
        await self.handleMsg()
        await self.incomingMsg(message)
        return

    async def responseHandler(self, message):
        await self.handleMsg()
        await self.responseMsg(message)
        return

    async def handleMsg(self):
        db = sqlite3.connect('chat-hub.db')
        self.past_user_inputs.clear()
        self.generated_responses.clear()
        try:        
            self.cli_con = st.empty()
            self.srv_con = st.empty()
            self.srv_container = self.srv_con.container(border=True)
            self.cli_container = self.cli_con.container(border=True)
            
            cursor = db.cursor()
            cursor.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 12")
            messages = cursor.fetchall()
            messages.reverse()

            # Collect messages based on sender
            for message in messages:
                if message[1] == 'server':
                    self.generated_responses.append(message[2])
                else:
                    self.past_user_inputs.append(message[2])

            self.srv_state.write(self.generated_responses)
            self.cli_state.write(self.past_user_inputs)
            return

        except Exception as e:
            print(f"Error: {e}")    

    async def incomingMsg(self, message):
        try:    
            self.cli_stat = st.empty()
            self.cli_state = self.cli_stat.status(label="Incoming message", state="running", expanded=True)
            self.cli_state.write(message)
            return

        except Exception as e:
            print(f"Error: {e}")    

    async def responseMsg(self, message):
        try:
            self.srv_stat = st.empty()
            self.srv_state = self.srv_stat.status(label="Server Response", state="running", expanded=True)
            self.srv_state.write(message)
            return

        except Exception as e:
            print(f"Error: {e}")   

    def start_msg_thread(self):
        def start_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.handleMsg())
            loop.run_forever()

        server_thread = threading.Thread(target=start_loop)
        server_thread.daemon = True  # Optional: makes the thread exit when the main program exits
        server_thread.start() 

    def incomingMSG_thread(self, message):
        self.start_msg_thread()
        def start_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.incomingMsg(message))
            loop.run_forever()

        server_thread = threading.Thread(target=start_loop)
        server_thread.daemon = True  # Optional: makes the thread exit when the main program exits
        server_thread.start()
        
    def response_thread(self, message):
        self.start_msg_thread()
        def start_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.responseMsg(message))
            loop.run_forever()

        server_thread = threading.Thread(target=start_loop)
        server_thread.daemon = True  # Optional: makes the thread exit when the main program exits
        server_thread.start()

      