from datetime import datetime
import streamlit as st
from utils import OpenAIClient
from components import ChatInterface
from config import DEFAULT_SETTING
#import markdown2
#import pdfkit

def create_sidebar():
    """ Creación y configuración la sidebar de la app"""

    with st.sidebar:
        st.title("LibrerIA")
        st.markdown("*Biblioteca*")
        st.divider()

        st.markdown("⚙️Configuración")

        st.divider

        st.markdown("### 💬 Controles del Chat")

        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            ChatInterface.clear_chat()
        
        # Exportar chat a texto 
        if st.session_state.get('messages'):
            st.markdows("### 🗒️ Exportar Chat")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")

            filename = st.text_input(
                "Nombre del archivo: ",
                value= f"librerIA_chat_{timestamp}",
                help="Sin extensión",
            )

            if st.button(
                "💾Descargar chat",
                use_container_width=True,
                ):
                
                export_text = ChatInterface.export_chat()

                if not filename.endswith(".md"):
                    filename =f"{filename}.md"

                st.download_button(
                    "💾Confirmar descarga",
                    data=export_text,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
        
        st.divider()

        ## Source - https://stackoverflow.com/q
# Posted by yusuf, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-07, License - CC BY-SA 4.0

#filename = "sample.md"
#mode = "r"

#with open(filename, mode) as file:
#    markdown_text = file.read()

#html_text = markdown2.markdown(markdown_text)

#pdfkit.from_string(html_text, "output.pdf")



        





