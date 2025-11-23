import sys
sys.path.insert(0, '.')

from components.connection import Connection

def test():
    conn = Connection()
    
    print("🔍 Probando conexión...")
    if conn.test_connection():
        print("✅ Conexión exitosa!\n")
        
        print("📋 Obteniendo esquema de la base de datos...\n")
        schema = conn.get_schema_info()
        print(schema)
    else:
        print("❌ Error en la conexión")

if __name__ == "__main__":
    test()




    # Para probar el test hay que poner en la temrinal: python test_connection.py