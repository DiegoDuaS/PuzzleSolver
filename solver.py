import random
from collections import deque

piezas = [
    {"numero": 1, "existe": True},
    {"numero": 2, "existe": True},
    {"numero": 3, "existe": True},
    {"numero": 4, "existe": True},
    {"numero": 5, "existe": True},
    {"numero": 6, "existe": True},
    {"numero": 7, "existe": True},
    {"numero": 8, "existe": True},
    {"numero": 9, "existe": True},
    {"numero": 10, "existe": True},
]

uniones = [
    {"numero": 11, "tipo": "hembra"},
    {"numero": 12, "tipo": "hembra"},
    {"numero": 21, "tipo": "macho"},
    {"numero": 22, "tipo": "macho"},
    {"numero": 23, "tipo": "hembra"},
    {"numero": 31, "tipo": "macho"},
    {"numero": 32, "tipo": "hembra"},
    {"numero": 33, "tipo": "hembra"},
    {"numero": 41, "tipo": "macho"},
    {"numero": 51, "tipo": "macho"},
    {"numero": 52, "tipo": "hembra"},
    {"numero": 53, "tipo": "hembra"},
    {"numero": 54, "tipo": "hembra"},
    {"numero": 55, "tipo": "hembra"},
    {"numero": 56, "tipo": "macho"},
    {"numero": 61, "tipo": "macho"},
    {"numero": 71, "tipo": "macho"},
    {"numero": 72, "tipo": "macho"},
    {"numero": 73, "tipo": "hembra"},
    {"numero": 81, "tipo": "macho"},
    {"numero": 82, "tipo": "hembra"},
    {"numero": 83, "tipo": "hembra"},
]

relaciones = [
    {"from": "Piece", "from_numero": 1, "to": "Union", "to_numero": 11, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 1, "to": "Union", "to_numero": 12, "tipo": "TIENE_UNION"},
    
    {"from": "Piece", "from_numero": 2, "to": "Union", "to_numero": 21, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 2, "to": "Union", "to_numero": 22, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 2, "to": "Union", "to_numero": 23, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 11, "to": "Union", "to_numero": 21, "tipo": "CONECTA_CON"},
    
    {"from": "Piece", "from_numero": 3, "to": "Union", "to_numero": 31, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 3, "to": "Union", "to_numero": 32, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 3, "to": "Union", "to_numero": 32, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 12, "to": "Union", "to_numero": 31, "tipo": "CONECTA_CON"},
    {"from": "Union", "from_numero": 33, "to": "Union", "to_numero": 22, "tipo": "CONECTA_CON"},
    
    {"from": "Piece", "from_numero": 4, "to": "Union", "to_numero": 41, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 41, "to": "Union", "to_numero": 55, "tipo": "CONECTA_CON"},
    
    {"from": "Piece", "from_numero": 5, "to": "Union", "to_numero": 51, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 5, "to": "Union", "to_numero": 52, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 5, "to": "Union", "to_numero": 53, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 5, "to": "Union", "to_numero": 54, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 5, "to": "Union", "to_numero": 55, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 5, "to": "Union", "to_numero": 56, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 56, "to": "Union", "to_numero": 23, "tipo": "CONECTA_CON"},
    {"from": "Union", "from_numero": 51, "to": "Union", "to_numero": 32, "tipo": "CONECTA_CON"},
    
     {"from": "Piece", "from_numero": 6, "to": "Union", "to_numero": 61, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 61, "to": "Union", "to_numero": 52, "tipo": "CONECTA_CON"},
    
    {"from": "Piece", "from_numero": 7, "to": "Union", "to_numero": 71, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 7, "to": "Union", "to_numero": 72, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 7, "to": "Union", "to_numero": 73, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 71, "to": "Union", "to_numero": 54, "tipo": "CONECTA_CON"},
    
   {"from": "Piece", "from_numero": 8, "to": "Union", "to_numero": 81, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 8, "to": "Union", "to_numero": 82, "tipo": "TIENE_UNION"},
    {"from": "Piece", "from_numero": 8, "to": "Union", "to_numero": 83, "tipo": "TIENE_UNION"},
    {"from": "Union", "from_numero": 81, "to": "Union", "to_numero": 53, "tipo": "CONECTA_CON"},
    {"from": "Union", "from_numero": 83, "to": "Union", "to_numero": 72, "tipo": "CONECTA_CON"},
]

union_a_pieza = {}
pieza_a_uniones = {}
union_a_conexiones = {}

for rel in relaciones:
    if rel["tipo"] == "TIENE_UNION":
        union_a_pieza[rel["to_numero"]] = rel["from_numero"]
        pieza_a_uniones.setdefault(rel["from_numero"], set()).add(rel["to_numero"])
    elif rel["tipo"] == "CONECTA_CON":
        union_a_conexiones.setdefault(rel["from_numero"], []).append(rel["to_numero"])
        union_a_conexiones.setdefault(rel["to_numero"], []).append(rel["from_numero"])  # Asumimos bidireccional

pieza_random = random.choice(piezas)
print(f"Pieza inicial seleccionada: {pieza_random['numero']}")

union_a_pieza = {}
for rel in relaciones:
    if rel["tipo"] == "TIENE_UNION":
        union_a_pieza[rel["to_numero"]] = rel["from_numero"]

# Mapa de union -> uniones conectadas
union_a_conexiones = {}
for rel in relaciones:
    if rel["tipo"] == "CONECTA_CON":
        union_a_conexiones.setdefault(rel["from_numero"], []).append(rel["to_numero"])
        
def resolver_con_pasos(pieza_inicio):
    visitadas_piezas = set()
    visitadas_uniones = set()
    pasos = []
    
    queue = deque()
    queue.append((pieza_inicio["numero"], []))  # (pieza_actual, camino)

    while queue:
        pieza_actual, camino = queue.popleft()

        if pieza_actual in visitadas_piezas:
            continue

        visitadas_piezas.add(pieza_actual)

        for u in pieza_a_uniones.get(pieza_actual, []):
            visitadas_uniones.add(u)

            for u_conectada in union_a_conexiones.get(u, []):
                if u_conectada in visitadas_uniones:
                    continue
                visitadas_uniones.add(u_conectada)

                pieza_vecina = union_a_pieza.get(u_conectada)
                if pieza_vecina and pieza_vecina not in visitadas_piezas:
                    paso = camino + [f"Pieza {pieza_actual} → Unión {u} → Unión {u_conectada} → Pieza {pieza_vecina}"]
                    pasos.append(paso[-1])
                    queue.append((pieza_vecina, paso))

    return pasos

# === Ejecutar ===
pasos_encontrados = resolver_con_pasos(pieza_random)

if pasos_encontrados:
    print("✅ Pasos encontrados para conectar piezas:\n")
    for paso in pasos_encontrados:
        print(f"🔗 {paso}")
else:
    print("❌ No se encontraron piezas conectadas.")