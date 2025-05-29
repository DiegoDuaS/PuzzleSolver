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

#Test de conexión
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

#Obtener una pieza random
def obtener_pieza_random(tx, name_puzzle):
    result = tx.run("""
        MATCH (p:Piezas)
        WHERE p.existe = true AND p.nombre_rompecabezas = $name_puzzle
        RETURN p.Numero AS numero
    """, name_puzzle=name_puzzle)
    piezas = [record["numero"] for record in result]
    return random.choice(piezas) if piezas else None

#Obtener las conexiones de piezas  
def obtener_conexiones(tx, numero_pieza, name_puzzle):
    result = tx.run("""
        MATCH (p:Piezas {Numero: $numero})
        MATCH (p)-[:TIENE]->(u:Union)-[:CONECTA]->(u2:Union)<-[:TIENE]-(p2:Piezas)
        WHERE p.existe = true AND p.nombre_rompecabezas = $name_puzzle AND u.nombre_rompecabezas = $name_puzzle AND u2.nombre_rompecabezas = $name_puzzle
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

#Obtener las conexiones de piezas perdidas 
def obtener_conexiones_lost(tx, numero_pieza, name_puzzle):
    result = tx.run("""
        MATCH (p:Piezas {Numero: $numero})
        MATCH (p)-[:TIENE]->(u:Union)-[:CONECTA]->(u2:Union)<-[:TIENE]-(p2:Piezas)
        WHERE p.nombre_rompecabezas = $name_puzzle AND u.nombre_rompecabezas = $name_puzzle AND u2.nombre_rompecabezas = $name_puzzle
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
    
#Funcion para verificar si pieza no esta perdida
def verificar_pieza_existe(tx, numero_pieza, name_puzzle):
    result = tx.run("""
        MATCH (p:Piezas {Numero: $numero, nombre_rompecabezas: $name_puzzle})
        RETURN p.existe AS existe
    """, numero=numero_pieza, name_puzzle=name_puzzle)
    record = result.single()
    return record["existe"] if record else False  # Devuelve False si no encuentra la pieza

#Funcion para descomponer el codigo de la union
def descomponer_union(codigo_union):
    codigo_str = str(codigo_union).zfill(3) 
    union = codigo_str[0]                   
    pieza = codigo_str[1:]                 
    return union, pieza

def main(puzzle_name):
    piezas_puestas_completamente = set()
    piezas_puestas_parcialmente = set()
    piezas_por_revisar = []
    piezas_perdidas = []

    uniones_procesadas = set()

    with driver.session() as session:
        complete = True
        # Elegir pieza inicial
        pieza_inicial = 7
        #pieza_inicial = session.execute_read(obtener_pieza_random, puzzle_name)
        if not pieza_inicial:
            print("No hay piezas disponibles.")
            return

        #Inicar con la pieza inicial
        print(f"🧩 Empezando con la pieza {pieza_inicial}, colócala en el tablero")
        piezas_puestas_parcialmente.add(pieza_inicial)
        piezas_por_revisar.append(pieza_inicial)
        #Loop principal
        while True:
            #Revisa las piezas para encontrar sus conexiones
            while piezas_por_revisar:
                pieza_actual = piezas_por_revisar.pop(0)
                
                #Decirle al usaro si coloca la pieza, o ya se encuentra en el tablero
                if pieza_actual in piezas_puestas_parcialmente:
                    print(f"\n🧩 La pieza {pieza_actual} ya se encuentra en el tablero")
                else:
                    print(f"\n🧩 Coloca la pieza {pieza_actual} en el tablero")
                
                # Se obtienen las conexiones de la pieza
                conexiones = session.execute_read(obtener_conexiones, pieza_actual, puzzle_name)
                if not conexiones:
                    print(f"Sin conexiones encontradas para pieza {pieza_actual}")
                    piezas_puestas_parcialmente.discard(pieza_actual)
                    piezas_puestas_completamente.add(pieza_actual)
                    continue

                nuevas_conexiones = False

                # Loop para cada conexion de la pieza
                for conexion in conexiones:
                    pieza_destino = conexion["pieza"]
                    existe_destino = session.execute_read(verificar_pieza_existe, pieza_destino, puzzle_name)
                    union_origen_codigo = conexion["union_origen"]
                    union_destino_codigo = conexion["union_destino"]
                    
                    union_origen, pieza_origen = descomponer_union(union_origen_codigo)
                    union_destino, pieza_destino_union = descomponer_union(union_destino_codigo)
                    
                    #En caso de que la pieza destino esta perdida
                    if not existe_destino:
                        if pieza_destino not in piezas_perdidas:
                            piezas_perdidas.append(pieza_destino)
                        print(f"   ↳ Se conectaría a pieza {pieza_destino}, pero está perdida (unión {union_origen} de pieza {pieza_origen} deberia de quedarse vacia)")
                        nuevas_conexiones = True
                        complete = False
                        continue 

                    #Guardar las uniones para no imprimirlas mas de una vez
                    id_union = tuple(sorted(((pieza_origen, union_origen), (pieza_destino_union, union_destino))))

                    if id_union in uniones_procesadas:
                        continue

                    # Marca esta unión como procesada
                    uniones_procesadas.add(id_union)
                    
                    # Impresion en casos de que la pieza esta en el tablero o no
                    if pieza_destino in piezas_puestas_parcialmente:
                        print(f"   ↳ Se conecta a pieza {pieza_destino}, que ya se encuentra en el tablero (unión {union_origen} de pieza {pieza_origen} → unión {union_destino} de pieza {pieza_destino_union})")
                    else:
                        print(f"   ↳ Se conecta a pieza {pieza_destino}, colócala en el tablero (unión {union_origen} de pieza {pieza_origen} → unión {union_destino} de pieza {pieza_destino_union})")

                    # Si la pieza destino no ha terminado todas sus conexiones
                    if pieza_destino not in piezas_puestas_completamente and pieza_destino not in piezas_puestas_parcialmente:
                        piezas_puestas_parcialmente.add(pieza_destino)
                        piezas_por_revisar.append(pieza_destino)

                # Si no hay nuevas conexiones para esta pieza, marcamos como completamente puesta
                if not nuevas_conexiones:
                    piezas_puestas_parcialmente.discard(pieza_actual)
                    piezas_puestas_completamente.add(pieza_actual)
                    print(f"*** Pieza {pieza_actual} completamente puesta ***")
            
            # Si no se encontraron piezas perdidas, se termina el loop principal
            if not piezas_perdidas:
                break
            
            # En caso de que si se encuentren piezas perdidas 
            nuevas_descubiertas = False
            for pieza_perdida in piezas_perdidas:
                # Encontrar las conexiones de esta pieza perdida
                conexiones = session.execute_read(obtener_conexiones_lost, pieza_perdida, puzzle_name)
                for conexion in conexiones:
                    pieza_destino = conexion["pieza"]
                    # En caso de que la pieza destino ya se encuentra puesta en el tablero
                    if pieza_destino in piezas_puestas_completamente or pieza_destino in piezas_puestas_parcialmente:
                        continue 
                    
                    # En caso de que la pieza destino no se encuentra en el tablero
                    print(f"\n🧩 Coloca la pieza {pieza_destino} en el tablero")
                    union_origen_codigo = conexion["union_origen"]
                    union_destino_codigo = conexion["union_destino"]
                    union_origen, pieza_origen = descomponer_union(union_origen_codigo)
                    union_destino, pieza_destino_union = descomponer_union(union_destino_codigo)

                    print(f"   ↳ Se conectaría a pieza {pieza_perdida}, pero está perdida (unión {union_destino} de pieza {pieza_destino_union} debería quedarse vacía)")
                    # Agregar a piezas por revisar en caso de que estas tengan mas conexiones
                    piezas_puestas_parcialmente.add(pieza_destino)
                    piezas_por_revisar.append(pieza_destino)
                    nuevas_descubiertas = True
            
            # En caso de que no se encuentran piezas que no esten en tablero, se termina el loop principal
            if not nuevas_descubiertas:
                break

        #Impresiones en casos de rompecabezas completo y rompecabezas con piezas faltantes
        if (complete):
            print("\n¡Rompecabezas Completado!")
        else:
            print("\n¡Rompecabezas Completado Parcialmente!")



if __name__ == "__main__":
    main("Puzzle Cohete")