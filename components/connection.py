from typing import Any, Dict, List
import pymssql

class Connection:
        
    def __init__(self):
        """Inicializa los parámetros de conexión"""
        self.server = 'PC-DESPACHO:1433'  # El nombre qye hay que cambiar, en clase es A407PC11:1433
        self.user = 'sa'
        self.password = 'tiger'
        self.database = 'Pubs'
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establece la conexión con la base de datos"""
        try:
            if not self.conn:
                self.conn = pymssql.connect(
                    server=self.server,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def get_schema_info(self) -> str:
        """
        Obtiene información real del esquema desde SQL Server
        
        Returns:
            str: Descripción del esquema
        """
        if not self.connect():
            return "Error: No se pudo conectar a la base de datos"
        
        try:
            # Consulta para obtener todas las tablas y sus columnas
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
            
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            
            # Organizar la información
            schema_info = "BASE DE DATOS: Pubs (Microsoft SQL Server)\n\n"
            schema_info += "ESTRUCTURA DE TABLAS:\n\n"
            
            current_table = None
            for row in rows:
                table_name = row[0]
                column_name = row[1]
                data_type = row[2]
                max_length = row[3] if row[3] else ''
                is_nullable = row[4]
                
                if current_table != table_name:
                    current_table = table_name
                    schema_info += f"\n{table_name}:\n"
                
                nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                length_info = f"({max_length})" if max_length else ""
                schema_info += f"  - {column_name}: {data_type}{length_info} {nullable}\n"
            
            return schema_info
            
        except Exception as e:
            return f"Error obteniendo esquema: {e}"
        finally:
            self.disconnect()
    
    def execute_query(self, sql: str) -> List[Dict[str, Any]]:  ##Hay que hacer import de estos tres, ctrl + . y te propone.
        """
        Ejecuta una consulta SQL y devuelve resultados
        (OPCIONAL: para probar las consultas generadas)
        """
        if not self.connect():
            return [{"error": "No se pudo conectar"}]
        
        try:
            self.cursor.execute(sql)
            columns = [desc[0] for desc in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        
        except Exception as e:
            return [{"error": str(e)}]
        finally:
            self.disconnect()
    
    def test_connection(self) -> bool:
        """Prueba la conexión"""
        try:
            if self.connect():
                self.cursor.execute("SELECT 1")
                result = self.cursor.fetchone()
                self.disconnect()
                return result[0] == 1
            return False
        except Exception as e:
            print(f"Error: {e}")
            return False