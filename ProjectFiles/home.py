import os
import asyncio
import http.server
import conteneiro
import socketserver
import streamlit as st

inputs = []
states = []
servers = []
clients = []
outputs = []
messages = []
intentios = []
used_ports = []
connections = []
server_ports = []
client_ports = []

st.set_page_config(layout="wide")

if "client_state" not in st.session_state:
    st.session_state.client_state = "complete"
if "server_state" not in st.session_state:
    st.session_state.server_state = "complete"        

stat1 = st.empty()
stat2 = st.empty()
cont = st.sidebar.empty()
server_status = stat1.status(label="websocket servers", state=st.session_state.server_state, expanded=False)
server_status.write(conteneiro.servers)
client_status = stat2.status(label="websocket clients", state=st.session_state.client_state, expanded=False)
client_status.write(conteneiro.clients)
side_status = cont.status(label="servers", state=st.session_state.server_state, expanded=False)

async def main():    

    # Inicjalizacja danych w st.session_state
    if "server_ports" not in st.session_state:
        st.session_state['server_ports'] = ""
    if "client_ports" not in st.session_state:
        st.session_state["client_ports"] = ""
    if "servers" not in st.session_state:
        st.session_state['servers'] = ""
    if "clients" not in st.session_state:
        st.session_state["clients"] = ""
    if "user_ID" not in st.session_state:
        st.session_state.user_ID = ""
    if "gradio_Port" not in st.session_state:
        st.session_state.gradio_Port = ""              
    if "googleAPI" not in st.session_state:
        st.session_state.googleAPI = ""
    if "cseID" not in st.session_state:
        st.session_state.cseID = ""
    if "server" not in st.session_state:
        st.session_state.server = False    
    if "client" not in st.session_state:
        st.session_state.client = False

    if st.session_state.server == True:
        stat1.empty()
        cont.empty()
        status1 = stat1.status(label="active servers", state="running", expanded=True)
        conte = cont.status(label="servers", state="running", expanded=True)
        status1.write(conteneiro.servers)
        conte.write(conteneiro.servers)

    if st.session_state.client == True:    
        stat2.empty()
        cont.empty()
        status2 = stat2.status(label="active clients", state="running", expanded=True)
        conte = cont.status(label="clients", state="running", expanded=True)
        status2.write(conteneiro.servers)
        conte.write(conteneiro.servers)

    st.title("NeuralGPT")

    c1, c2 = st.columns(2)

    with c1:
        st.text("Server ports")
        srv_state = st.empty()
        server_status1 = srv_state.status(label="active servers", state="complete", expanded=False)
        if st.session_state.server == True:
            server_status1.update(state="running", expanded=True)
            server_status1.write(conteneiro.servers)
    
    with c2:   
        st.text("Client ports")
        cli_state = st.empty()
        client_status1 = cli_state.status(label="active clients", state="complete", expanded=False)
        if st.session_state.client == True:    
            st.session_state.client_state = "running"
            client_status1.update(state="running", expanded=True)
            client_status1.write(conteneiro.clients)

    with st.sidebar:

        srv_sidebar = st.empty()
        cli_sidebar = st.empty()        
        server_status = srv_sidebar.status(label="los serveros", state="complete", expanded=False)
        client_status = cli_sidebar.status(label="los clientos", state="complete", expanded=False)
        server_status.write(conteneiro.servers)
        client_status.write(conteneiro.clients)

        if st.session_state.server == True:
            srv_sidebar.empty()
            server_status = srv_sidebar.status(label="servers", state="running", expanded=True)
            server_status.write(conteneiro.servers)

        if st.session_state.client == True:
            cli_sidebar.empty()
            client_status = cli_sidebar.status(label="clients", state="running", expanded=True)
            client_status.write(conteneiro.clients)

# Uruchomienie aplikacji
asyncio.run(main())