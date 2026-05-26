"""Hand-written implementations of the two Watts–Strogatz metrics.

This module computes, from scratch, the two structural quantities used
throughout the project:

* :func:`camí_mig`            — average shortest-path length :math:`L`.
* :func:`coef_clusterització` — global clustering coefficient
  (transitivity) :math:`C = 3 \\cdot \\#\\text{triangles} / \\#\\text{paths of length 2}`.
* :func:`nodes_within_distance` — internal helper used by the
  clustering routine; returns the multiset of nodes reachable in
  exactly ``dist`` steps from a source node (counted with multiplicity).

The function names are kept in Catalan because the unit tests in
``tests/test_unit_calculate_metrics.py`` import them by name; only the
docstrings, comments and report-side text are in English.

A NetworkX :class:`~networkx.Graph` is used only as a container; the
shortest-path search itself relies on the BFS helper
:func:`networkx.single_source_shortest_path_length`, which matches the
behaviour of our hand-rolled BFS but is implemented in C and therefore
fast enough for the ``N = 1000`` sweeps used by the *Metric analytics*
page in the documentation.
"""

import networkx as nx
import numpy as np
from src.smallworld.networks import build_all


def camí_mig(G: nx.Graph) -> float:
    """Average shortest-path length :math:`L` of ``G``.

    Computed as

    .. math::

        L \\;=\\; \\frac{1}{N(N-1)} \\sum_{i \\neq j} d(i, j),

    where :math:`d(i, j)` is the shortest-path distance found by BFS.
    If ``G`` is disconnected the function falls back to the **largest
    connected component**, because otherwise some pairwise distances
    would be infinite and :math:`L` undefined.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, unweighted graph.

    Returns
    -------
    float
        The average shortest-path length over all ordered pairs
        ``(i, j)`` with ``i != j`` in the (largest) connected component.

    Notes
    -----
    Equivalent to :func:`networkx.average_shortest_path_length` on a
    connected input (verified by the unit tests).
    """

    # If the graph is disconnected, restrict to its largest connected
    # component — otherwise we would have d(i, j) = ∞ for some pairs.
    if not nx.is_connected(G):
        G = G.subgraph(max(nx.connected_components(G), key=len))
        print("The graph is not connected...")
        print("Falling back to the largest connected component...\n")

    total = 0

    for node in G.nodes():
        # Dictionary {target: shortest distance} obtained by BFS.
        distances = nx.single_source_shortest_path_length(G, node)
        total += sum(distances.values())

    N = G.number_of_nodes()

    # Each (ordered) pair is visited exactly once, so the total number
    # of contributions is N * (N - 1).
    return total / (N * (N - 1))


def nodes_within_distance(G: nx.Graph, node: int, dist: int) -> list:
    """Return all nodes reachable from ``node`` in exactly ``dist`` steps.

    Walks expand one hop at a time, collecting neighbours **with
    multiplicity** — a node visited along two different length-``dist``
    walks therefore appears twice. This multiplicity is what
    :func:`coef_clusterització` relies on to count length-2 paths.

    Parameters
    ----------
    G : networkx.Graph
        Graph to traverse.
    node : int
        Source node.
    dist : int
        Number of steps to take. Must be ``>= 1``.

    Returns
    -------
    list[int]
        The multiset of endpoints of every length-``dist`` walk that
        starts at ``node``. May contain duplicates and may contain
        ``node`` itself when ``dist >= 2``.
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


def coef_clusterització(G: nx.Graph) -> float:
    """Global clustering coefficient (transitivity) of ``G``.

    Defined as

    .. math::

        C \\;=\\; \\frac{3 \\cdot \\#\\text{triangles}}
                       {\\#\\text{paths of length 2}},

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
        The global clustering coefficient. Equivalent to
        :func:`networkx.transitivity` (verified by the unit tests).
    """

    num_triangles = 0

    for node in G.nodes():
        nodes = nodes_within_distance(G, node, 3)
        for x in nodes:
            if x == node:
                num_triangles += 1

    # Every triangle is counted six times: once per vertex × two
    # directions of traversal.
    num_triangles = num_triangles // 6

    camins_long_2 = 0

    for node in G.nodes():
        num_neighbors = len(nodes_within_distance(G, node, 1))
        nodes = nodes_within_distance(G, node, 2)

        # From distance-1 neighbours we expand to distance-2 endpoints,
        # then subtract the walks that bounce back to the source.
        camins_long_2 += len(nodes) - num_neighbors

    # Each length-2 path is counted twice (once in each direction).
    camins_long_2 = camins_long_2 // 2

    # Each triangle contains three length-2 paths, hence the factor 3
    # in the numerator.
    coef = 3 * num_triangles / camins_long_2

    return coef


if __name__ == "__main__":
    N, k, beta = 50, 10, 0.1
    graphs = build_all(N=N, k=k, beta=beta, seed=42)

    metrics = {}

    print("\n---------------------------------------\n")

    for graph in graphs:
        metrics[graph] = {}
        metrics[graph]["L"] = camí_mig(graphs[graph])
        metrics[graph]["C"] = coef_clusterització(graphs[graph])
        print(f"Average path length for graph '{graph}': {metrics[graph]['L']:.4f}")
        print(f"Clustering coefficient for graph '{graph}': {metrics[graph]['C']:.4f}")
        print("\n---------------------------------------\n")
