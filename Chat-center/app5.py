import gradio as gr
import os
import sqlite3
import websockets
import json
import asyncio
import time

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI

os.chdir("E:/repos/")

async def connect_websocket():
    async with websockets.connect('ws://localhost:5000') as websocket:
        while True:
            message = await websocket.recv()
            # Process the received message
            response = process_message(message)
            await websocket.send(response)

def process_message(message):
    # Perform message processing logic here
    return 'Processed response'


def get_response(input, google_cse_id, google_api_key, openai_api_key):
    os.environ["GOOGLE_CSE_ID"] = google_cse_id
    os.environ["GOOGLE_API_KEY"] = google_api_key
    os.environ["OPENAI_API_KEY"] = openai_api_key

    llm = OpenAI(temperature=0)
    tools = load_tools(["google-search", "llm-math"], llm=llm)
    agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True, return_intermediate_steps=True)

    response = agent({"input": input})
    return response["output"], response["intermediate_steps"]

# Create a connection to the database
conn = sqlite3.connect('E:/repos/chatcenter/chat-hub.sql')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table to store user inputs and chatbot responses
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history';")
    result = cursor.fetchone()
    if not result:
        cursor.execute('''CREATE TABLE chat_history
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_input TEXT,
                        chatbot_response TEXT,
                        chatbot_name TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
except Exception as e:
    st.error(f"Error: {e}")


def on_submit(inputs):
    goal_output, intermediate_steps = get_response(*inputs)
    iface.set_output([goal_output, intermediate_steps])  
    send_response_to_server(goal_output),
iface = gr.Interface(
    fn=get_response, 
    inputs=[
        gr.Textbox(label="Goal definition:"),
        gr.Textbox(label="Google CSE - ID:", type="text"),
        gr.Textbox(label="Google API KEY:", type="password"),
        gr.Textbox(label="OpenAI API KEY:", placeholder="sk-...", type="password")
    ],
    outputs=[
        gr.Textbox(label="Goal output:"),
        gr.Json(label="Intermediate Steps")
    ],      
    
    title="GPT Agents Demo",
    description="Demo application of gpt-based agents including two tools (google-search and llm-math). The result and intermediate steps are included.",
    on_submit=on_submit
)

# Insert a sample record into the table
cursor.execute('''INSERT INTO chat_history (user_input, chatbot_response, chatbot_name)
                  VALUES (?, ?, ?)''', ('Hello', 'Hi there!', 'Chatbot 1'))

# Commit the changes to the database
conn.commit()

# Close the database connection
conn.close()

# error capturing in integration as a component

error_message = ""

try:
    iface.queue(concurrency_count=20)
    iface.launch(share=True, server_port=7862)

except Exception as e:
    error_message = "An error occurred: " + str(e)
    iface.outputs[1].value = error_message

asyncio.run(connect_websocket())