import streamlit as st
from utils import GeminiClient, OpenAIClient
from dotenv import load_dotenv
from components import connection
import re
import pandas as pd
from io import BytesIO

load_dotenv()

class ChatInterface:
    
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        """Iniciamos el estado de la sesion"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        if 'llm_client' not in st.session_state:
            try:
                st.session_state.llm_client = GeminiClient()
            except ValueError:
                st.session_state.llm_client = None
    
    def validate_sql(self, sql_text: str) -> tuple:
        """
        Valida que el SQL solo contenga SELECT
        
        Args:
            sql_text: El texto SQL a validar
            
        Returns:
            (bool, str): (es_valido, mensaje_error)
        """
        # Convertir a minúsculas 
        sql_lower = sql_text.lower()
        
        # Palabras prohibidas que modifican datos
        forbidden_keywords = [
            'insert', 'update', 'delete', 'drop', 'create', 'alter',
            'truncate', 'exec', 'execute', 'grant', 'revoke', 'merge',
            'sp_executesql', 'xp_cmdshell', 'bulk', 'restore', 'backup'
        ]
        
        # Verificar palabras prohibidas
        for keyword in forbidden_keywords:
            # Buscar la palabra completa (no como parte de otra palabra)
            if re.search(r'\b' + keyword + r'\b', sql_lower):
                return False, f"⚠️ Operación prohibida: '{keyword.upper()}' no está permitido. Solo se permiten consultas SELECT de lectura."
        
        # Verificar que contenga SELECT
        if 'select' not in sql_lower:
            return False, "⚠️ La respuesta debe contener una consulta SELECT."
        
        return True, ""

    def handle_user_input(self):
        """Entrada del usuario y genera la respuesta"""
        if prompt := st.chat_input("Escribe tu consulta sobre la base de datos"):
            # Mostrar mensaje del usuario
            with st.chat_message("user"):
                st.markdown(prompt)

            # Añadir al historial
            self.add_message("user", prompt)

            temperature = st.session_state.temperature
            max_tokens = st.session_state.max_tokens

            # Generar respuesta
            if st.session_state.llm_client:
                with st.chat_message("assistant"):
                    st.caption(f"Usando: temperature={temperature} - max_tokens={max_tokens}")
                    with st.spinner("Generando consulta SQL..."):
                        # Crear el contexto del prompt
                        context = self._create_context(prompt)
                        response = st.session_state.llm_client.generate_response(
                            context,
                            st.session_state.messages,
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                        
                        full_response = ""
                        response_widget = st.empty()
                        
                        for chunk in response:
                            if chunk:
                                full_response += chunk
                                response_widget.markdown(full_response)
                        
                        # Validar SQL generado
                        is_valid, error_msg = self.validate_sql(full_response)
                        if not is_valid:
                            st.error(error_msg)
                            st.warning("🔒 Solo consultas de lectura (SELECT)!")
                            full_response = f"❌ **CONSULTA BLOQUEADA**\n\n{error_msg}\n\n---\n\n*Consulta generada (bloqueada):*\n```sql\n{full_response}\n```"
                        else:
                            st.success("✅ Consulta validada - Solo lectura")

                        self.add_message("assistant", full_response)    
            else:
                with st.chat_message("assistant"):
                    error_msg = "⚠️ No se pudo conectar con el servidor de IA. Verifica la configuración"
                    st.error(error_msg)
                    self.add_message("assistant", error_msg)
    
    def _create_context(self, user_prompt: str) -> str:
        """
        Crea el contexto para el prompt con información de la BBDD

        Args:
            user_prompt: La pregunta del usuario

        Returns:
            prompt completo con el contexto
        """
        # Obtener la información del esquema de la base de datos
        conn = connection.Connection()
        schema_info = conn.get_schema_info()

        context = f"""
Eres LibrerIA, un experto en SQL Server especializado en generar consultas SOLO DE LECTURA para la base de datos Pubs.

{schema_info}

⚠️ RESTRICCIONES CRÍTICAS - MUY IMPORTANTE:
1. SOLO puedes generar consultas SELECT
2. Está ABSOLUTAMENTE PROHIBIDO usar:
   - INSERT, UPDATE, DELETE (modifican datos)
   - DROP, CREATE, ALTER, TRUNCATE (modifican estructura)
   - EXEC, EXECUTE, MERGE (ejecutan procedimientos)
   - Cualquier comando que modifique la base de datos
3. Si el usuario pide modificar, insertar, actualizar o eliminar datos, debes responder:
   "No puedo generar esa consulta. Solo puedo crear consultas SELECT de lectura."

INSTRUCCIONES:
- Genera ÚNICAMENTE consultas SELECT
- Usa sintaxis de SQL Server (T-SQL)
- Si necesitas JOINs, usa las relaciones correctas
- Devuelve solo el código SQL sin explicaciones adicionales
- Si la pregunta no se puede responder con las tablas disponibles, explica por qué

Pregunta del usuario: {user_prompt}

Genera la consulta SQL SELECT:
"""
        return context
    
    def add_message(self, role: str, msg: str):
        """ Añade el mensaje al historial """
        st.session_state.messages.append({
            "role": role,
            "message": msg
        })

    def display_messages(self):
        """ Muestra todos los mensajes del chat """
        for idx, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                st.markdown(message["message"])
                
                # Si es un mensaje del asistente, buscar código SQL
                if message["role"] == "assistant":
                    sql_code = self._extract_sql(message["message"])
                    if sql_code:
                        # Botones de acción
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 3])
                        
                        with col1:
                            if st.button("▶️ Ejecutar", key=f"exec_{idx}", help="Ejecutar consulta"):
                                self._execute_and_show_results(sql_code, idx)
                        
                        with col2:
                            with st.popover("📋 Ver SQL"):
                                st.code(sql_code, language="sql")
                                st.caption("Selecciona y copia con Ctrl+C")
                        
                        with col3:
                            # Botón para descargar SQL
                            st.download_button(
                                "💾 SQL",
                                data=sql_code,
                                file_name=f"query_{idx}.sql",
                                mime="text/plain",
                                key=f"download_sql_{idx}",
                                help="Descargar consulta"
                            )
    
    def _extract_sql(self, text: str) -> str:
        """
        Extrae código SQL del mensaje
        
        Args:
            text: Texto del mensaje
            
        Returns:
            str: Código SQL encontrado o cadena vacía
        """
        # Buscar código SQL en bloques de código markdown
        sql_pattern = r'```sql\n(.*?)\n```'
        match = re.search(sql_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Buscar SELECT directamente
        if 'SELECT' in text.upper():
            lines = text.split('\n')
            sql_lines = []
            in_sql = False
            
            for line in lines:
                if 'SELECT' in line.upper():
                    in_sql = True
                if in_sql:
                    sql_lines.append(line)
                    if ';' in line:
                        break
            
            if sql_lines:
                return '\n'.join(sql_lines).strip()
        
        return ""
    


    # ESTE METODO HAY QUE   PULIRLO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    def _execute_and_show_results(self, sql_code: str, idx: int):
        """
        Ejecuta la consulta SQL y muestra los resultados
        
        Args:
            sql_code: Código SQL a ejecutar
            idx: Índice del mensaje para keys únicos
        """
        # Validar que sea SELECT
        is_valid, error_msg = self.validate_sql(sql_code)
        
        if not is_valid:
            st.error(error_msg)
            st.warning("🔒 Solo se permiten consultas SELECT")
            return
        
        # Contenedor para los resultados
        with st.container():
            with st.spinner("🔄 Ejecutando consulta en la base de datos..."):
                try:
                    conn = connection.Connection()
                    results = conn.execute_query(sql_code)
                    
                    if not results:
                        st.info("ℹ️ La consulta no devolvió resultados")
                        return
                    
                    # Verificar si hay error
                    if len(results) == 1 and 'error' in results[0]:
                        st.error(f"❌ Error en SQL: {results[0]['error']}")
                        with st.expander("🔍 Ver detalles"):
                            st.code(sql_code, language="sql")
                        return
                    
                    # Convertir a DataFrame
                    df = pd.DataFrame(results)
                    
                    # Banner de éxito con métricas
                    st.success("✅ Consulta ejecutada correctamente")
                    
                    # Métricas en cards más visibles
                    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                    with metric_col1:
                        st.metric(
                            label="📊 Filas",
                            value=f"{len(df):,}",
                            help="Número total de registros"
                        )
                    with metric_col2:
                        st.metric(
                            label="📋 Columnas", 
                            value=len(df.columns),
                            help="Número de campos"
                        )
                    with metric_col3:
                        size_kb = df.memory_usage(deep=True).sum() / 1024
                        st.metric(
                            label="💾 Tamaño",
                            value=f"{size_kb:.1f} KB",
                            help="Memoria utilizada"
                        )
                    with metric_col4:
                        st.metric(
                            label="⏱️ Estado",
                            value="Completo",
                            delta="OK",
                            delta_color="normal"
                        )
                    
                    st.divider()
                    
                    # Tabs mejoradas
                    tab1, tab2, tab3 = st.tabs([
                        "📊 Resultados",
                        "📈 Estadísticas", 
                        "💾 Exportar"
                    ])
                    
                    with tab1:
                        st.markdown("### 📋 Tabla de resultados")
                        
                        # Dataframe con configuración mejorada
                        st.dataframe(
                            df,
                            use_container_width=True,
                            height=min(600, len(df) * 35 + 38),  # Altura dinámica
                            column_config={
                                col: st.column_config.TextColumn(
                                    col,
                                    width="medium",
                                    help=f"Columna: {col}"
                                ) for col in df.columns
                            }
                        )
                        
                        # Información adicional
                        st.caption(f"Mostrando {len(df)} registro(s) con {len(df.columns)} columna(s)")
                    
                    with tab2:
                        st.markdown("### 📊 Análisis de datos")
                        
                        # Dividir en dos columnas
                        stats_col1, stats_col2 = st.columns(2)
                        
                        with stats_col1:
                            st.markdown("**📉 Estadísticas numéricas:**")
                            numeric_cols = df.select_dtypes(include=['number']).columns
                            if len(numeric_cols) > 0:
                                st.dataframe(
                                    df[numeric_cols].describe(),
                                    use_container_width=True
                                )
                            else:
                                st.info("No hay columnas numéricas para analizar")
                        
                        with stats_col2:
                            st.markdown("**🔍 Información de columnas:**")
                            
                            # Crear tabla de info más legible
                            info_data = []
                            for col in df.columns:
                                info_data.append({
                                    'Columna': col,
                                    'Tipo': str(df[col].dtype),
                                    'Únicos': df[col].nunique(),
                                    'Nulos': df[col].isna().sum(),
                                    'No Nulos': df[col].notna().sum()
                                })
                            
                            info_df = pd.DataFrame(info_data)
                            st.dataframe(
                                info_df,
                                use_container_width=True,
                                hide_index=True,
                                column_config={
                                    "Columna": st.column_config.TextColumn("Columna", width="medium"),
                                    "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                                    "Únicos": st.column_config.NumberColumn("Únicos", width="small"),
                                    "Nulos": st.column_config.NumberColumn("Nulos", width="small"),
                                    "No Nulos": st.column_config.NumberColumn("No Nulos", width="small"),
                                }
                            )
                        
                        # Muestra de datos
                        st.markdown("**🎲 Primeras 5 filas:**")
                        st.dataframe(df.head(), use_container_width=True)
                    
                    with tab3:
                        st.markdown("### 💾 Opciones de exportación")
                        st.info("Descarga los resultados en diferentes formatos")
                        
                        # Crear columnas para los botones
                        export_col1, export_col2, export_col3 = st.columns(3)
                        
                        with export_col1:
                            st.markdown("**📄 CSV**")
                            st.caption("Archivo de texto separado por comas")
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="⬇️ Descargar CSV",
                                data=csv,
                                file_name=f"libreria_resultados_{idx}.csv",
                                mime="text/csv",
                                key=f"download_csv_{idx}",
                                use_container_width=True
                            )
                        
                        with export_col2:
                            st.markdown("**📊 Excel**")
                            st.caption("Libro de Excel compatible")
                            try:
                                buffer = BytesIO()
                                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                    df.to_excel(writer, index=False, sheet_name='Resultados')
                                
                                st.download_button(
                                    label="⬇️ Descargar Excel",
                                    data=buffer.getvalue(),
                                    file_name=f"libreria_resultados_{idx}.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key=f"download_excel_{idx}",
                                    use_container_width=True
                                )
                            except ImportError:
                                st.error("⚠️ openpyxl no está instalado")
                                st.code("pip install openpyxl", language="bash")
                        
                        with export_col3:
                            st.markdown("**📋 JSON**")
                            st.caption("Formato de datos estructurado")
                            json_str = df.to_json(orient='records', indent=2)
                            st.download_button(
                                label="⬇️ Descargar JSON",
                                data=json_str,
                                file_name=f"libreria_resultados_{idx}.json",
                                mime="application/json",
                                key=f"download_json_{idx}",
                                use_container_width=True
                            )
                        
                        st.divider()
                        
                        # Vista previa del formato
                        with st.expander("👁️ Vista previa de formatos"):
                            preview_tab1, preview_tab2, preview_tab3 = st.tabs(["CSV", "JSON", "Info"])
                            
                            with preview_tab1:
                                st.code(df.head(3).to_csv(index=False), language="text")
                            
                            with preview_tab2:
                                st.code(df.head(3).to_json(orient='records', indent=2), language="json")
                            
                            with preview_tab3:
                                st.text(f"Total de registros: {len(df)}")
                                st.text(f"Total de columnas: {len(df.columns)}")
                                st.text(f"Columnas: {', '.join(df.columns)}")
                    
                except Exception as e:
                    st.error(f"❌ Error al ejecutar la consulta")
                    
                    # Mostrar error detallado
                    with st.expander("🔍 Ver detalles técnicos del error", expanded=True):
                        st.code(str(e), language="text")
                        st.markdown("**Consulta SQL:**")
                        st.code(sql_code, language="sql")
                        
                        # Sugerencias
                        st.markdown("**💡 Posibles soluciones:**")
                        st.markdown("""
                        - Verifica que la sintaxis SQL sea correcta
                        - Comprueba que las tablas y columnas existan
                        - Revisa la conexión a la base de datos
                        - Asegúrate de que solo uses SELECT
                        """)
    @staticmethod
    def export_chat():
        """
        Exporta el historial del chat como texto
        
        Returns:
            El historial del chat formateado
        """
        if not st.session_state.messages:
            return "No hay mensajes para exportar"
        
        export_text = "# Historial de Chat - LibrerIA\n\n"

        for i, message in enumerate(st.session_state.messages):
            role = "👤 Usuario" if message["role"] == "user" else "🤖 LibrerIA"
            export_text += f"## Mensaje {i+1} - {role}\n\n"
            export_text += f"{message['message']}\n\n"
            export_text += f"---\n\n"
        
        return export_text
    
    @staticmethod
    def clear_chat():
        st.session_state.messages = []
        st.rerun()
