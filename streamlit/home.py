import asyncio
import streamlit as st

servers = {}
inputs = []
outputs = []
used_ports = []
server_ports = []
client_ports = []

st.set_page_config(layout="wide")

st.session_state.update(st.session_state)

if 'active_page' not in st.session_state:
    st.session_state.active_page = 'NeuralGPT'
if "sidebar" not in st.session_state:
    st.session_state.sidebar = True
if "server_Ports" not in st.session_state:
    st.session_state['server_ports'] = False
if "client_Ports" not in st.session_state:
    st.session_state['client_ports'] = False
if "userID" not in st.session_state:
    st.session_state.userID = False

st.sidebar.title("NeuralGPT")
st.sidebar.info(
    """
    [GitHub](https://github.com/giswqs)
    """
)

async def main():
    st.text("Server ports:")
    serverPorts = st.sidebar.container(border=True)
    serverPorts.markdown(st.session_state['server_ports'])
    st.sidebar.text("Client ports")
    clientPorts = st.sidebar.container(border=True)
    clientPorts.markdown(st.session_state['client_ports'])
    st.sidebar.text("Charavter.ai ID")
    user_id = st.sidebar.container(border=True)
    user_id.markdown(st.session_state.userID)

    st.title("NeuralGPT")

    st.markdown(
        """
        This page is supposed to work as interface of a hierarchical cooperative multi-agent framework/platform called NeuralGPT

        """
    )

    st.info("Click on the left sidebar menu to navigate to the different apps.")

    st.subheader("shit goes in here")
    st.markdown(
        """
        The following stuff is totally random no need to think about it too much.
    """
    )

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:

        st.image("https://i.postimg.cc/gk0LXT5p/earth6.gif")             
        st.image("https://i.postimg.cc/kM2d2NcZ/movie-18.gif")
        st.image("https://i.postimg.cc/8z5ccf7z/Screenshot-2022-03-02-21-27-22-566-com-google-android-youtube.jpg")
        st.image("https://i.postimg.cc/YqvTSppw/dh.gif")
        st.image("https://i.postimg.cc/7PdxPGhr/bandicam-2018-11-13-04-33-29-245.jpg")

    with row1_col2:
        st.image("https://i.postimg.cc/X7nw1tFT/Neural-GPT.gif")
        st.image("https://i.postimg.cc/qBwpKMVh/brain-cell-galaxy.jpg")
        st.image("https://i.postimg.cc/T1sdWCL2/pyth.png")
        st.image("https://i.postimg.cc/L8T5s9Gk/bandicam2023-02-0323-10-40-545-ezgif-com-speed.gif")
        st.image("https://i.postimg.cc/rF5zvCJP/clocks5.gif")

asyncio.run(main())    