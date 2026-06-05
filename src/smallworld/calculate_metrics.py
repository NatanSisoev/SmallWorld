"""Hand-written implementations of the two Watts-Strogatz metrics.

This module computes, from scratch, the two structural quantities used
throughout the project:

* `average_path_length` — average shortest-path length $L$.
* `clustering_coefficient` — global clustering coefficient
  (transitivity) $C = 3 \cdot \#\text{triangles} / \#\text{paths of length 2}$.
* `nodes_at_distance` — internal helper used by the
  clustering routine; returns the multiset of nodes reachable in
  exactly ``dist`` steps from a source node (counted with multiplicity).
"""

from collections import deque

import networkx as nx
from src.smallworld.networks import build_all


def average_path_length(G: nx.Graph) -> float:
    r"""Average shortest-path length $L$ of ``G``.

    Computed as

    $$L = \frac{1}{N(N-1)} \sum_{i \neq j} d(i, j)$$

    where $d(i, j)$ is the shortest-path distance found by a hand-written
    BFS. If ``G`` is disconnected the function silently restricts to the
    **largest connected component**, because otherwise some pairwise
    distances would be infinite and $L$ undefined.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, unweighted graph.

    Returns
    -------
    float
        Average shortest-path length over all ordered pairs ``(i, j)``
        with ``i != j`` in the (largest) connected component.
        Returns ``0.0`` for a single-node component.

    Notes
    -----
    On a connected graph this is equivalent to
    `networkx.average_shortest_path_length` (verified by the unit tests).
    The BFS is hand-written as required by the project's "by-hand core
    algorithms" convention.
    """

    if not nx.is_connected(G):
        G = G.subgraph(max(nx.connected_components(G), key=len))

    N = G.number_of_nodes()
    if N <= 1:
        return 0.0

    total = 0

    for node in G.nodes():
        distances = _bfs_distances(G, node)
        total += sum(distances.values())

    return total / (N * (N - 1))


def _bfs_distances(G: nx.Graph, source: int) -> dict[int, int]:
    """Shortest-path distances from ``source`` using a hand-written BFS."""
    distances = {source: 0}
    queue = deque([source])

    while queue:
        node = queue.popleft()
        next_distance = distances[node] + 1
        for neighbor in G.neighbors(node):
            if neighbor not in distances:
                distances[neighbor] = next_distance
                queue.append(neighbor)

    return distances


def nodes_at_distance(G: nx.Graph, node: int, dist: int) -> list:
    """Return all nodes reachable from ``node`` in exactly ``dist`` steps.

    Walks expand one hop at a time, collecting neighbours **with
    multiplicity** — a node visited along two different length-``dist``
    walks therefore appears twice. This multiplicity is what
    `clustering_coefficient` relies on to count length-2 paths.

    Parameters
    ----------
    G : networkx.Graph
        Graph to traverse.
    node : int
        Source node.
    dist : int
        Number of hops to take. Pass ``1`` to get immediate neighbours
        (identical to ``list(G.neighbors(node))``). Pass ``2`` to get
        all length-2 walk endpoints (with multiplicity) for clustering.

    Returns
    -------
    list[int]
        Multiset of walk endpoints after exactly ``dist`` hops from
        ``node``. May contain duplicates and may contain ``node`` itself
        when ``dist >= 2``.
    """

    neighbors = list(G.neighbors(node))
    i = 1

    while i < dist:
        new_neighbors = []
        for neighbor in neighbors:
            new_neighbors.extend(G.neighbors(neighbor))
        neighbors = new_neighbors
        i += 1

    return neighbors


def clustering_coefficient(G: nx.Graph) -> float:
    r"""Global clustering coefficient (transitivity) of ``G``.

    Defined as

    $$C = \frac{3 \cdot \#\text{triangles}}{\#\text{paths of length 2}}$$

    i.e. the fraction of length-2 paths that close into a triangle.
    This is the *global* (transitivity) definition, **not** the
    average-local clustering used in the original Watts–Strogatz
    paper; both live in ``[0, 1]`` but differ on heterogeneous graphs.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, unweighted graph.

    Returns
    -------
    float
        The global clustering coefficient in ``[0, 1]``. Returns ``0.0``
        if the graph has no paths of length 2 (e.g. a tree with all
        nodes of degree ≤ 1). Equivalent to `networkx.transitivity`
        (verified by the unit tests).
    """

    neighbor_sets = {node: set(G.neighbors(node)) for node in G.nodes()}
    closed_two_paths = 0
    total_two_paths = 0

    for center, neighbors_set in neighbor_sets.items():
        neighbors = list(neighbors_set)
        degree = len(neighbors)
        total_two_paths += degree * (degree - 1)

        for i, u in enumerate(neighbors):
            for v in neighbors[i + 1:]:
                if v in neighbor_sets[u]:
                    closed_two_paths += 2

    if total_two_paths == 0:
        return 0.0
    return closed_two_paths / total_two_paths


if __name__ == "__main__":
    N, k, beta = 50, 10, 0.1
    graphs = build_all(N=N, k=k, beta=beta, seed=42)

    metrics = {}

    print("\n---------------------------------------\n")

    for graph in graphs:
        metrics[graph] = {}
        metrics[graph]["L"] = average_path_length(graphs[graph])
        metrics[graph]["C"] = clustering_coefficient(graphs[graph])
        print(f"Average path length for graph '{graph}': {metrics[graph]['L']:.4f}")
        print(f"Clustering coefficient for graph '{graph}': {metrics[graph]['C']:.4f}")
        print("\n---------------------------------------\n")
