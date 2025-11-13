from datetime import datetime
import streamlit as st
from utils import GeminiClient, OpenAIClient
from components import ChatInterface
from config import DEFAULT_SETTINGS

#instalo librerias nuevas markdown2 pdfkit y weasyprint

import markdown2
import pdfkit
from weasyprint import HTML

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
        
        # Exportar chat a PDF 
        if st.session_state.get('messages'):
            st.markdows("### 🗒️ Exportar Chat")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            nombre_archivo = f"librerIA_chat:{timestamp}.pdf"

            if st.button(
                "💾Descargar chat",
                use_container_width=True,
                ):
                try:
                    markdown_text = ChatInterface.export_chat()
                    html_text = markdown2.markdown(markdown_text)

                    pdf_data = HTML(string=html_text).write_pdf()

                    st.download_button(
                        "💾Confirmar descarga",
                        data=pdf_data,
                        file_name=nombre_archivo,
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")
        
        st.divider()



        






