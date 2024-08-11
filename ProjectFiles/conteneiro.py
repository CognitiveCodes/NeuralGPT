import re
import os
import datetime
import sqlite3
import websockets
import json
import asyncio
import time
import threading
import streamlit as st

servers = []
clients = []
inputs = []
outputs = []
messages = []
used_ports = []
server_ports = []
client_ports = []    

stat1 = st.empty()
stat2 = st.empty()
cont = st.sidebar.empty()

class container:

    def __init__(self):

        self.server = None
        self.client = None
        self.srv_name = ""
        self.cli_name = ""
        self.servers = []        
        self.clients = []
        self.messages = []
        self.observers = []
        self.clientMsg = []
        self.serverMsg = []
        self.past_user_inputs = []
        self.generated_responses = []
        self.incoming_messages = []
        self.outgoing_messages = []
        self.lock = threading.Lock()

        c1, c2 = st.columns(2)

        with c1:
            self.srv_con = st.empty()
            self.srv_container = self.srv_con.container(border=True)
            self.stat = st.empty()
            self.srv_state = self.stat.status(label="Llama3", state="complete", expanded=False)

        with c2:
            self.cli_con = st.empty()
            self.cli_container = self.cli_con.container(border=True)
            self.stat1 = st.empty()
            self.cli_state = self.stat1.status(label="Llama3", state="complete", expanded=False)

        with st.sidebar:
            self.stat2 = st.empty()
            self.state2 = self.stat2.status(label="Llama3", state="complete", expanded=False)

    def append(self, item):
        with self.lock:
            self.messages.append(item)

    def pop(self, index=0):
        with self.lock:
            return self.messages.pop(index)

    def is_empty(self):
        with self.lock:
            return len(self.messages) == 0
        
    def append_incoming(self, message):
        with self.lock:
            self.incoming_messages.append(message)

    def append_outgoing(self, message):
        with self.lock:
            self.outgoing_messages.append(message)

    def get_all_incoming(self):
        with self.lock:
            return list(self.incoming_messages)

    def get_all_outgoing(self):
        with self.lock:
            return list(self.outgoing_messages)

    def handleMsg(self, msg):
        self.past_user_inputs.clear()
        self.generated_responses.clear()
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

        for message in messages:
            self.messages.append(message[2])

container_instance = container()
