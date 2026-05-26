import networkx as nx
import numpy as np
from src.smallworld.networks import build_all


def camí_mig(G: nx.Graph) -> float: 

    # Si el graf no és connex, prenem el subgraf connex amb el major nombre de nodes.
    # Si no, obtindríem una distància infinita.
    if not nx.is_connected(G):
        G = G.subgraph(max(nx.connected_components(G), key = len))
        print("El graf no és connex...")
        print("Generant subgraf connex maximal...\n")

    total = 0

    for node in G.nodes():
        distances = nx.single_source_shortest_path_length(G, node) # Retorna diccionari amb distàncies mínimes a tots els nodes (BFS).
        total += sum(distances.values())

    N = G.number_of_nodes()

    # La distància entre cada parell de nodes es calcula dues vegades, pel que el nombre total de distàncies calculades és N * (N - 1).
    return total / (N * (N - 1))


def nodes_within_distance(G: nx.Graph, node: int, dist: int) -> list:

    # Aquesta funció et retorna la llista de nodes de {G} als quals pots arribar amb {dist} passos des de {node}.

    neighbors = list(G.neighbors(node))
    i = 1

    while i < dist:
        new_neighbors = []
        for neighbor in neighbors:
            new_neighbors.extend(G.neighbors(neighbor))
        neighbors = new_neighbors
        i += 1
    
    return neighbors


def coef_clusterització(G: nx.Graph) -> float:

    num_triangles = 0

    for node in G.nodes():
        nodes = nodes_within_distance(G, node, 3)
        for x in nodes:
            if x == node:
                num_triangles += 1

    # Cada triangle es compta 6 vegades: partint des de cada vèrtex del triangle, i en ambdós sentits.
    num_triangles = num_triangles // 6

    camins_long_2 = 0

    for node in G.nodes():
        num_neighbors = len(nodes_within_distance(G, node, 1))
        nodes = nodes_within_distance(G, node, 2)

        # Des dels nodes a distància 1, calculem tots els veïns (distància 2) i restem els camins que tornen al node original.
        camins_long_2 += len(nodes) - num_neighbors
    
    # Cada camí de longitud 2 es compta 2 vegades (un cop en cada sentit).
    camins_long_2 = camins_long_2 // 2

    # Per a cada camí de longitud 2, necessitem comptar si aquest pertany a un triangle tancat.
    # Com un triangle tancat té 3 camins de longitud 2, necessitem multiplicar per 3 el nombre de triangles per obtenir el coeficient correcte.
    coef = 3 * num_triangles / camins_long_2

    return coef
    

if __name__ == "__main__":
    N, k, beta = 50, 10, 0.1
    graphs = build_all(N = N, k = k, beta = beta, seed = 42)

    metrics = {}

    print("\n---------------------------------------\n")

    for graph in graphs: 
        metrics[graph] = {}
        metrics[graph]["L"] = camí_mig(graphs[graph])
        metrics[graph]["C"] = coef_clusterització(graphs[graph])
        print(f"El camí mig pel graf '{graph}' és: {metrics[graph]["L"]:.4f}")
        print(f"El coeficient de clusterització del graf '{graph}' és: {metrics[graph]["C"]:.4f}")
        print("\n---------------------------------------\n")