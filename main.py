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

def obtener_pieza_random(tx, name_puzzle):
    result = tx.run("""
        MATCH (p:Piezas)
        WHERE p.existe = true AND p.nombre_rompecabezas = $name_puzzle
        RETURN p.Numero AS numero
    """, name_puzzle=name_puzzle)
    piezas = [record["numero"] for record in result]
    return random.choice(piezas) if piezas else None

def obtener_conexiones(tx, numero_pieza, name_puzzle):
    result = tx.run("""
        MATCH (p:Piezas {Numero: $numero})
        MATCH (p)-[:TIENE]->(u:Union)-[:CONECTA]->(u2:Union)<-[:TIENE]-(p2:Piezas)
        WHERE p2.existe = true AND p.nombre_rompecabezas = $name_puzzle
        RETURN DISTINCT p2.Numero AS conectado, u.Numero AS union_origen, u2.Numero AS union_destino
    """, numero=numero_pieza, name_puzzle=name_puzzle)
    return [
        {
            "pieza": record["conectado"],
            "union_origen": record["union_origen"],
            "union_destino": record["union_destino"]
        }
        for record in result
    ]

def descomponer_union(codigo_union):
    codigo_str = str(codigo_union).zfill(3) 
    union = codigo_str[0]                   
    pieza = codigo_str[1:]                 
    return union, pieza

def main(puzzle_name):
    piezas_puestas_completamente = set()
    piezas_puestas_parcialmente = set()
    piezas_por_revisar = []

    uniones_procesadas = set()

    with driver.session() as session:
        complete = True
        # Elegir pieza inicial
        pieza_inicial = session.execute_read(obtener_pieza_random, puzzle_name)
        if not pieza_inicial:
            print("No hay piezas disponibles.")
            return

        print(f"🧩 Empezando con la pieza {pieza_inicial}, colócala en el tablero")
        piezas_puestas_parcialmente.add(pieza_inicial)
        piezas_por_revisar.append(pieza_inicial)

        while piezas_por_revisar:
            pieza_actual = piezas_por_revisar.pop(0)
            
            if pieza_actual in piezas_puestas_parcialmente:
                print(f"🧩 La pieza {pieza_actual} ya se encuentra en el tablero")
            else:
                print(f"🧩 Coloca la pieza {pieza_actual} en el tablero")
            
            conexiones = session.execute_read(obtener_conexiones, pieza_actual, puzzle_name)
            if not conexiones:
                print(f"Sin conexiones encontradas para pieza {pieza_actual}")
                piezas_puestas_parcialmente.discard(pieza_actual)
                piezas_puestas_completamente.add(pieza_actual)
                continue

            nuevas_conexiones = False

            for conexion in conexiones:
                pieza_destino = conexion["pieza"]
                existe_destino = conexion.get("existe", True) 
                
                if not existe_destino:
                    print(f" La pieza {pieza_destino} está perdida, se omite")
                    nuevas_conexiones = True
                    complete = False
                    continue 

                union_origen_codigo = conexion["union_origen"]
                union_destino_codigo = conexion["union_destino"]
                union_origen, pieza_origen = descomponer_union(union_origen_codigo)
                union_destino, pieza_destino_union = descomponer_union(union_destino_codigo)

                id_union = tuple(sorted(((pieza_origen, union_origen), (pieza_destino_union, union_destino))))

                if id_union in uniones_procesadas:
                    continue

                # Marca esta unión como procesada
                uniones_procesadas.add(id_union)
                
                if pieza_destino in piezas_puestas_parcialmente:
                    print(f"   ↳ Se conecta a pieza {pieza_destino}, que ya se encuentra en el tablero (unión {union_origen} de pieza {pieza_origen} → unión {union_destino} de pieza {pieza_destino_union})")
                else:
                    print(f"   ↳ Se conecta a pieza {pieza_destino}, colócala en el tablero (unión {union_origen} de pieza {pieza_origen} → unión {union_destino} de pieza {pieza_destino_union})")

                if pieza_destino not in piezas_puestas_completamente and pieza_destino not in piezas_puestas_parcialmente:
                    piezas_puestas_parcialmente.add(pieza_destino)
                    piezas_por_revisar.append(pieza_destino)

            # Si no hay nuevas conexiones para esta pieza, marcamos como completamente puesta
            if not nuevas_conexiones:
                piezas_puestas_parcialmente.discard(pieza_actual)
                piezas_puestas_completamente.add(pieza_actual)
                print(f"*** Pieza {pieza_actual} completamente puesta ***")

        if (complete):
            print("\n¡Rompecabezas Completado!")
        else:
            print("\n¡Rompecabezas Completado Parcialmente!")



if __name__ == "__main__":
    main("Puzzle Real")