from neo4j import GraphDatabase, RoutingControl
from dotenv import load_dotenv
import os
import random

# Cargar variables del archivo .env
load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
AUTH = (USER, PASSWORD)

driver = GraphDatabase.driver(URI, auth=AUTH)

def test_connection():
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 AS test")
            value = result.single()["test"]
            print(f"✅ Conexión exitosa. Resultado de prueba: {value}")
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    test_connection()
    
