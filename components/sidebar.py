from datetime import datetime
import streamlit as st
from .chat_interface import ChatInterface
from .connection import Connection
from config import DEFAULT_SETTINGS
from utils.api_client import GeminiClient, OpenAIClient  
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch



# SUSTITUYO ESTO POR REPORTLAB
# #instalo librerias nuevas markdown2 pdfkit y weasyprint
# import markdown2 
# from weasyprint import HTML

# def create_sidebar():
#     """ Creación y configuración la sidebar de la app"""

#     with st.sidebar:
#         st.title("LibrerIA")
#         st.markdown("*Biblioteca*")
#         st.divider()

#         st.markdown("⚙️Configuración")

#         st.divider

#         st.markdown("### 💬 Controles del Chat")

#         if st.button("🗑️ Limpiar Chat", use_container_width=True):
#             ChatInterface.clear_chat()
        
#         # Exportar chat a PDF 
#         if st.session_state.get('messages'):
#             st.markdown("### 🗒️ Exportar Chat")

#             timestamp = datetime.now().strftime("%Y%m%d_%H%M")
#             nombre_archivo = f"librerIA_chat:{timestamp}.pdf"

#             if st.button(
#                 "💾Descargar chat",
#                 use_container_width=True,
#                 ):
#                 try:
#                     markdown_text = ChatInterface.export_chat()
#                     html_text = markdown2.markdown(markdown_text)

#                     pdf_data = HTML(string=html_text).write_pdf()

#                     st.download_button(
#                         "💾Confirmar descarga",
#                         data=pdf_data,
#                         file_name=nombre_archivo,
#                         mime="application/pdf",
#                         use_container_width=True
#                     )
#                 except Exception as e:
#                     st.error(f"Error al generar PDF: {e}")
        
#         st.divider()





def create_sidebar():
    with st.sidebar:
        st.title("LibrerIA")
        st.markdown("*Biblioteca*")
        st.divider()

        st.info("🔒 Solo consultas SELECT")
        st.divider()

         # Botón para ver esquema
        if st.button("📊 Ver Esquema de BD", use_container_width=True):
            st.session_state.show_schema = not st.session_state.get('show_schema', False)
       
        st.divider()
       
        st.markdown("### ⚙️ Configuración del Modelo")
        
        # ✅ AGREGAR CONTROLES:
        st.session_state.temperature = st.slider(
            "🌡️ Temperature",
            min_value=0.0,
            max_value=2.0,
            value=DEFAULT_SETTINGS["temperature"],
            step=0.1,
            help="Controla la creatividad de las respuestas. Valores bajos = más predecible, valores altos = más creativo"
        )
        
        st.session_state.max_tokens = st.slider(
            "📝 Max Tokens",
            min_value=100,
            max_value=10000,
            value=DEFAULT_SETTINGS["max_tokens"],
            step=100,
            help="Número máximo de tokens en la respuesta"
        )

        st.divider()
        st.markdown("### 💬 Controles del Chat")

        # Agregarmos los controles


        if st.button("🗑️ Limpiar Chat", use_container_width=True):
            ChatInterface.clear_chat()
        
        if st.session_state.get('messages'):
            st.markdown("### 📥 Exportar Chat")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            
            # Obtener el texto del chat
            markdown_text = ChatInterface.export_chat()
            
        # BOTON PARA TEXTO en txt
            st.download_button(
                "💾 Descargar historial",
                data=markdown_text,
                file_name=f"librerIA_chat_{timestamp}.txt",
                mime="text/plain",
                use_container_width=True
            )

            # BOTON PARA PDF
            if st.button("📄 Generar PDF", use_container_width=True):
                try:
                    pdf_data = generate_pdf(st.session_state.messages)
                    
                    st.download_button(
                        "💾 Confirmar descarga PDF",
                        data=pdf_data,
                        file_name=f"librerIA_chat_{timestamp}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error al generar PDF: {e}")
        
        st.divider()     

def display_schema_modal():
    """Muestra el esquema de la base de datos en la página principal"""
    if st.session_state.get('show_schema', False):
        with st.expander("📊 **ESQUEMA DE BASE DE DATOS - Pubs**", expanded=True):
            try:
                conn = Connection()
                schema_info = conn.get_schema_info()
                
                # Crear tabs para mejor organización
                tab1, tab2 = st.tabs(["📋 Texto completo", "🔍 Por tabla"])
                
                with tab1:
                    st.code(schema_info, language="sql")
                    
                    # Botón para copiar
                    if st.button("📋 Copiar esquema completo"):
                        st.code(schema_info)
                        st.success("✅ Copiado al portapapeles (usa Ctrl+C)")
                
                with tab2:
                    # Obtener tablas dinámicamente
                    tables = get_tables_info(conn)
                    
                    if tables:
                        selected_table = st.selectbox(
                            "Selecciona una tabla:",
                            options=list(tables.keys())
                        )
                        
                        if selected_table:
                            st.markdown(f"### 📁 Tabla: `{selected_table}`")
                            
                            # Mostrar columnas en formato tabla
                            cols_data = []
                            for col in tables[selected_table]:
                                cols_data.append({
                                    "Columna": col['name'],
                                    "Tipo": col['type'],
                                    "Nulo": "Sí" if col['nullable'] == "YES" else "No"
                                })
                            
                            st.dataframe(cols_data, use_container_width=True)
                            
                            # Ejemplo de consulta
                            sample_query = f"SELECT * FROM {selected_table};"
                            st.markdown("**📝 Consulta de ejemplo:**")
                            st.code(sample_query, language="sql")
                
                # Botón para cerrar
                if st.button("❌ Cerrar esquema"):
                    st.session_state.show_schema = False
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error al obtener esquema: {e}")


def get_tables_info(conn):
    """
    Obtiene información estructurada de las tablas
    
    Returns:
        dict: Diccionario con tablas y sus columnas
    """
    try:
        if not conn.connect():
            return {}
        
        query = """
        SELECT 
            t.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.IS_NULLABLE
        FROM INFORMATION_SCHEMA.TABLES t
        JOIN INFORMATION_SCHEMA.COLUMNS c ON t.TABLE_NAME = c.TABLE_NAME
        WHERE t.TABLE_TYPE = 'BASE TABLE'
        ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION
        """
        
        conn.cursor.execute(query)
        rows = conn.cursor.fetchall()
        
        # Organizar por tablas
        tables = {}
        for row in rows:
            table_name = row[0]
            if table_name not in tables:
                tables[table_name] = []
            tables[table_name].append({
                'columna': row[1],
                'tipo': row[2],
                'nulo': row[3]
            })
        
        
        conn.disconnect()
        # Mostrar cada tabla
        for table_name, columns in tables.items():
            st.markdown(f"**📁 {table_name}**")
            for col in columns:
                nullable = "✓" if col['nulo'] == "YES" else "✗"
                st.text(f"  • {col['columna']}: {col['tipo']} (NULL: {nullable})")
            st.markdown("---")
        else:
            st.error("No se pudo conectar a la BD")
        
    except Exception as e:
        st.error(f"Error obteniendo tablas: {e}")
        return {}


def add_copy_button_to_messages():
    """
    Añade botones de copiar SQL a los mensajes del chat
    Debe llamarse desde el chat_interface.py
    """
    pass  




def generate_pdf(messages):
    """
    Genera un PDF del historial de chat usando ReportLab
    
    Args:
        messages: Lista de mensajes del chat
        
    Returns:
        bytes: Datos del PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Historial de Chat - LibrerIA", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 0.3*inch))
    
    # Mensajes
    for i, message in enumerate(messages, 1):
        role = "👤 Usuario" if message["role"] == "user" else "🤖 LibrerIA"
        
        # Encabezado del mensaje
        header = Paragraph(
            f"<b>Mensaje {i} - {role}</b>",
            styles['Heading2']
        )
        story.append(header)
        
        # Contenido (escapar caracteres especiales y reemplazar saltos de línea)
        content_text = message['message'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        content_text = content_text.replace('\n', '<br/>')
        
        content = Paragraph(content_text, styles['Normal'])
        story.append(content)
        story.append(Spacer(1, 0.2*inch))
    
    # Construir PDF
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data


def _display_connection_status(provider: str):
    """
    Muestra el estado de conexión con el proveedor de IA.
    Args:
    provider: El proveedor seleccionado ('Gemini' o 'OpenAI').
    """
    try:
        if provider == "Gemini":
            client = GeminiClient()

            if client.api_key:
                st.success("✅ Gemini conectado")
                st.session_state.llm_client = client
            else:
                st.error("❌ Gemini no configurado")
        elif provider == "OpenAI":
            client = OpenAIClient()
            if client.api_key:
                st.success("✅ OpenAI conectado")
                st.session_state.llm_client = client
            else:
                st.error("❌ OpenAI no configurado")

    except ValueError as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Configura tu clave de API en el archivo .env")





