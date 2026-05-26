"""Tests for calculate_metrics file"""

import pytest
import networkx as nx
import numpy as np

from src.smallworld.networks import build_all, build_ring
from src.smallworld.calculate_metrics import (
    camí_mig,
    nodes_within_distance,
    coef_clusterització,
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


# ------------ Camí mig ------------

def test_cami_mig_return_type(ring: nx.Graph):
    assert isinstance(camí_mig(ring), float)

def test_cami_mig_k5_is_one(k5: nx.Graph):
    """In K5 every pair of nodes is directly connected, so L = 1."""
    assert camí_mig(k5) == pytest.approx(1.0)

def test_cami_mig_cycle6(cycle6: nx.Graph):
    """C6: distances from each node sum to 1+2+3+2+1 = 9, total 6*9 = 54,
    divided by N*(N-1) = 30, gives L = 1.8."""
    assert camí_mig(cycle6) == pytest.approx(1.8)

def test_cami_mig_matches_networkx(ring: nx.Graph):
    """Compare against networkx's reference implementation."""
    assert camí_mig(ring) == pytest.approx(nx.average_shortest_path_length(ring))

def test_cami_mig_disconnected_uses_largest_component(disconnected: nx.Graph):
    """On a disconnected graph the function falls back to the largest CC.
    Both triangles have L = 1, so the result must be 1.0."""
    assert camí_mig(disconnected) == pytest.approx(1.0)

def test_cami_mig_non_negative(ring: nx.Graph):
    assert camí_mig(ring) >= 0.0


# ------------ Nodes Within Distance ------------

def test_dist_one_returns_neighbours(ring: nx.Graph):
    """At distance 1 the function must return exactly the node's neighbours."""
    node = list(ring.nodes)[0]
    result = nodes_within_distance(ring, node, 1)
    assert sorted(result) == sorted(ring.neighbors(node))

def test_dist_one_k5(k5: nx.Graph):
    """In K5 every node has the other 4 as neighbours."""
    result = nodes_within_distance(k5, 0, 1)
    assert sorted(result) == [1, 2, 3, 4]

def test_dist_two_contains_original_node(k5: nx.Graph):
    """In K5, two-step walks can return to the origin
    (origin -> neighbour -> origin)."""
    result = nodes_within_distance(k5, 0, 2)
    assert 0 in result

def test_dist_returns_list(ring: nx.Graph):
    assert isinstance(nodes_within_distance(ring, 0, 1), list)

def test_dist_two_ring_count(cycle6: nx.Graph):
    """In a 2-regular cycle, each neighbour has 2 neighbours, so two-step
    walks yield 2 * 2 = 4 entries (with multiplicity)."""
    result = nodes_within_distance(cycle6, 0, 2)
    assert len(result) == 4


# ------------ Coeficient de Clusterització ------------

def test_clustering_return_type(ring: nx.Graph):
    assert isinstance(coef_clusterització(ring), float)

def test_clustering_k5_is_one(k5: nx.Graph):
    """K5 is fully connected: every length-2 path closes a triangle, C = 1."""
    assert coef_clusterització(k5) == pytest.approx(1.0)

def test_clustering_matches_networkx_transitivity(ring: nx.Graph):
    """The metric implemented is the global clustering (transitivity):
    3 * triangles / paths-of-length-2. Compare against networkx."""
    assert coef_clusterització(ring) == pytest.approx(nx.transitivity(ring))

def test_clustering_in_unit_interval(ring: nx.Graph):
    c = coef_clusterització(ring)
    assert 0.0 <= c <= 1.0

def test_clustering_complete_graph_k4():
    """Every complete graph Kn (n >= 3) has clustering coefficient 1."""
    K4 = nx.complete_graph(4)
    assert coef_clusterització(K4) == pytest.approx(1.0)
