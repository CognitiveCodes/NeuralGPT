import asyncio
import streamlit as st

server_ports = []
client_ports = []

# Inicjalizacja danych w st.session_state
if "server_ports" not in st.session_state:
    st.session_state['server_ports'] = ""
if "client_ports" not in st.session_state:
    st.session_state['client_ports'] = ""
if "user_ID" not in st.session_state:
    st.session_state.user_ID = ""
if "gradio_Port" not in st.session_state:
    st.session_state.gradio_Port = "" 
if "server" not in st.session_state:
    st.session_state.server = False
if "client" not in st.session_state:
    st.session_state.client = False     

st.set_page_config(layout="wide")

async def main():

    st.title("NeuralGPT")
        
    gradio_Ports = st.container(border=True)
    gradio_Ports.markdown(st.session_state.gradio_Port)    

    with st.sidebar:
        # Wyświetlanie danych, które mogą być modyfikowane na różnych stronach
        serverPorts = st.container(border=True)
        serverPorts.markdown(st.session_state['server_ports'])
        st.text("Client ports")
        clientPorts = st.container(border=True)
        clientPorts.markdown(st.session_state['client_ports'])
        st.text("Character.ai ID")
        user_id = st.container(border=True)
        user_id.markdown(st.session_state.user_ID)
        status = st.status(label="runs", state="complete", expanded=False)

        if st.session_state.server == True:
            st.markdown("server running...")
        
        if st.session_state.client == True:    
            st.markdown("client running")

# Uruchomienie aplikacji
asyncio.run(main())
