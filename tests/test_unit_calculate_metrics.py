"""Tests for calculate_metrics module."""

import pytest
import networkx as nx
import numpy as np

from src.smallworld.networks import build_all, build_ring
from src.smallworld.calculate_metrics import (
    average_path_length,
    nodes_at_distance,
    clustering_coefficient,
)


@pytest.fixture(scope="module")
def ring():
    """Small ring graph shared across tests."""
    return build_all(N=20, k=4, seed=42)["ring"]


@pytest.fixture
def k5():
    """Complete graph K5 — useful for analytically known values."""
    return nx.complete_graph(5)


@pytest.fixture
def cycle6():
    """Cycle C6 — ring lattice with k=2 and N=6, known analytic values."""
    return build_ring(N=6, k=2)


@pytest.fixture
def disconnected():
    """Two disjoint triangles — disconnected graph for robustness tests."""
    G = nx.Graph()
    G.add_edges_from([(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3)])
    return G


# ------------ Average Path Length (camí_mig) ------------

def test_average_path_length_return_type(ring: nx.Graph):
    assert isinstance(average_path_length(ring), float)

def test_average_path_length_k5_is_one(k5: nx.Graph):
    """In K5 every pair of nodes is directly connected, so L = 1."""
    assert average_path_length(k5) == pytest.approx(1.0)

def test_average_path_length_cycle6(cycle6: nx.Graph):
    """C6: distances from each node sum to 1+2+3+2+1 = 9, total 6*9 = 54,
    divided by N*(N-1) = 30, gives L = 1.8."""
    assert average_path_length(cycle6) == pytest.approx(1.8)

def test_average_path_length_matches_networkx(ring: nx.Graph):
    """Compare against networkx's reference implementation."""
    assert average_path_length(ring) == pytest.approx(nx.average_shortest_path_length(ring))

def test_average_path_length_disconnected_uses_largest_component(disconnected: nx.Graph):
    """On a disconnected graph the function falls back to the largest CC.
    Both triangles have L = 1, so the result must be 1.0."""
    assert average_path_length(disconnected) == pytest.approx(1.0)

def test_average_path_length_non_negative(ring: nx.Graph):
    assert average_path_length(ring) >= 0.0


# ------------ Nodes at Distance (nodes_within_distance) ------------

def test_distance_one_returns_neighbours(ring: nx.Graph):
    """At distance 1 the function must return exactly the node's neighbours."""
    node = list(ring.nodes)[0]
    result = nodes_at_distance(ring, node, 1)
    assert sorted(result) == sorted(ring.neighbors(node))

def test_distance_one_k5(k5: nx.Graph):
    """In K5 every node has the other 4 as neighbours."""
    result = nodes_at_distance(k5, 0, 1)
    assert sorted(result) == [1, 2, 3, 4]

def test_distance_two_contains_original_node(k5: nx.Graph):
    """In K5, two-step walks can return to the origin
    (origin -> neighbour -> origin)."""
    result = nodes_at_distance(k5, 0, 2)
    assert 0 in result

def test_distance_returns_list(ring: nx.Graph):
    assert isinstance(nodes_at_distance(ring, 0, 1), list)

def test_distance_two_ring_count(cycle6: nx.Graph):
    """In a 2-regular cycle, each neighbour has 2 neighbours, so two-step
    walks yield 2 * 2 = 4 entries (with multiplicity)."""
    result = nodes_at_distance(cycle6, 0, 2)
    assert len(result) == 4


# ------------ Clustering Coefficient (coef_clusterització) ------------

def test_clustering_coefficient_return_type(ring: nx.Graph):
    assert isinstance(clustering_coefficient(ring), float)

def test_clustering_coefficient_k5_is_one(k5: nx.Graph):
    """K5 is fully connected: every length-2 path closes a triangle, C = 1."""
    assert clustering_coefficient(k5) == pytest.approx(1.0)

def test_clustering_coefficient_matches_networkx_transitivity(ring: nx.Graph):
    """The metric implemented is the global clustering (transitivity):
    3 * triangles / paths-of-length-2. Compare against networkx."""
    assert clustering_coefficient(ring) == pytest.approx(nx.transitivity(ring))

def test_clustering_coefficient_in_unit_interval(ring: nx.Graph):
    c = clustering_coefficient(ring)
    assert 0.0 <= c <= 1.0

def test_clustering_coefficient_complete_graph_k4():
    """Every complete graph Kn (n >= 3) has clustering coefficient 1."""
    K4 = nx.complete_graph(4)
    assert clustering_coefficient(K4) == pytest.approx(1.0)


# ------------ Tests verifying equivalence with NetworkX -----------

def test_average_path_length_vs_networkx_on_ring():
    """Verify hand-written BFS gives same result as NetworkX on ring graphs."""
    for N in [10, 20, 50]:
        for k in [4, 6]:
            G = build_ring(N=N, k=k)
            assert average_path_length(G) == pytest.approx(
                nx.average_shortest_path_length(G),
                rel=1e-10
            )

def test_clustering_coefficient_vs_networkx_on_multiple_graphs():
    """Verify clustering implementation matches NetworkX transitivity."""
    graphs = build_all(N=30, k=6, beta=0.01, seed=42)
    for name in ["ring", "er", "ws"]:
        G = graphs[name]
        assert clustering_coefficient(G) == pytest.approx(
            nx.transitivity(G),
            rel=1e-10
        )
