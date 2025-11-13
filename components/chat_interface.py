import streamlit as st
from utils import GeminiClient, OpenAIClient
from dotenv import load_dotenv


load_dotenv()

class ChatInterface:
    
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Iniciamos el estado de la sesion"""
        if 'messages' not in st.session_state:
            st.session_state.messages=[]

        if 'llm_client' not in st.session_state:
            try:
                st.session_state.llm_client = GeminiClient()
            except ValueError:
                st.session_state.llm_client = None
    
    def handle_user_input(self):
        """Entrada del usuario y genera la respuesta"""
        if prompt := st.chat_input("Escribe tu consulta"):
        #Enseñamos el mensaje del ususario
            with st.chat_message("user"):
                st.markdown(prompt)

            #Añadir al historial
            self.add_message("user",prompt)

            temperature = st.session_state.temperature
            max_tokens = st.session_state.max_tokens


            # Generar respuesta
            if st.session_state.llm_client:
                    with st.chat_message("assistant"):
                        st.caption(f"Usando: temperature={temperature} - max_tokens={max_tokens}")
                        with st.spinner("Pensando..."):
                            # Crear el contexto del prompt
                            context = self._create_context(prompt)
                            response = st.session_state.llm_client.generate_response(
                                context,
                                st.session_state.messages,
                                temperature=temperature,
                                max_tokens=max_tokens,
                            )
                            #st.write_stream(response)
                            full_response = ""
                            response_widget = st.empty()
                            for chunk in response:
                                if chunk:
                                    full_response += chunk
                                    response_widget.markdown(full_response)
                            self.add_message("assistant", full_response)
            else:
                with st.chat_message("assistant"):
                    error_msg="⚠️ No se pudo conectar con el servidor de IA. Verifica la configuración"
                    st.error(error_msg)
                    self.add_message("assistant", error_msg)
    
    def _create_context(self, user_prompt:str) -> str:
        """
        Crea el contexto para el prompt

        Args:
            user_prompt: La pregunta del usuario

        Returns:
            prompt completo con el contexto
        """

        context= f"""
        Eres LibrerIA, un asistente conectado a una base de datos -
        Tu objetivo es ayudar a clientes con sus preguntas sobre libros y autores y demas datos incluidos en la base de datos a la que estas conectado:

        1. Explicaciones claras y precisas
        2. Devolver las consultas a la BBDD en SQL puro como texto
        
        

        Pregunta del usuario: {user_prompt}

        Responde de manera útil y sencilla
"""
        return context
    
    def add_message(self, role:str, msg:str):
        """ Añade el mensaje al historial """
        st.session_state.messages.append({
            "role":role,
            "message":msg
        })


    def display_messages(self):
        """ Muestra todos los mensajes del chat """
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["message"])

    
    

    @staticmethod
    def export_chat():
        """

        Exporta el historial del chat como texto
        
        Returns:
            El historial ddel chat formateado

        """

        if not st.session_state.messages:
            return "No hay mensajes para exportar"
        
        export_text = "# Historial de Chat - LibrerIA\n\n"

        for i, message in enumerate(st.session_state.messages):
            role = "👸🏻 Usuario" if message["role"] == "user" else "🧙🏻‍♂️ LibrerIA"
            export_text += f"## Mensaje {i} - {role}\n\n"
            export_text += f"{message['message']}\n\n"
            export_text += f"---\n\n"
        
        return export_text
    
    @staticmethod
    def clear_chat():
        st.session_state.messages = []
        st.rerun()
