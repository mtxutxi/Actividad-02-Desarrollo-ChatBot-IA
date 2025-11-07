from components import ChatInterface, create_sidebar

import streamlit as st

st.set_page_config(
    page_title="LibrerIA",
    page_icon="🥁🤯",
    layout="centered",
    initial_sidebar_state="expanded"
)

create_sidebar()

st.title("LibrerIA")

chat = ChatInterface()

chat.display_messages()

chat.handle_user_input()