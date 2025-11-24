from components import ChatInterface, create_sidebar
from components.sidebar import display_schema_modal
from config import DEFAULT_SETTINGS
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

# TEMPORAL: para debug
st.write("🔍 Debug:")
st.write(f"API Key configurada: {bool(os.getenv('GEMINI_API_KEY'))}")
st.write(f"DEBUG - show_schema: {st.session_state.get('show_schema', False)}")


st.set_page_config(
    page_title="LibrerIA",
    page_icon="🥁🤯",
    layout="centered",
    initial_sidebar_state="expanded"
)

if 'temperature' not in st.session_state:
    st.session_state.temperature = DEFAULT_SETTINGS["temperature"]

if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = DEFAULT_SETTINGS["max_tokens"]

if 'show_schema' not in st.session_state:
    st.session_state.show_schema = False

create_sidebar()

st.title("📚LibrerIA")


# Mostrar esquema  de la base de datos
display_schema_modal()


# CHAT
chat = ChatInterface()

chat.display_messages()

chat.handle_user_input()

