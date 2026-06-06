"""Tests for the network builders and their equivalence with the NetworkX oracle.

The project's headline convention is that the graph constructors are written
by hand (``src.smallworld.networks``), with ``src.smallworld.networks_nx`` kept
as a reference oracle that delegates to NetworkX. These tests pin down the
builders' own contracts (degree, edge count, validation, reproducibility) and
verify equivalence with the oracle — exact for the ring lattice, statistical
for Erdős-Rényi and Watts-Strogatz.
"""

import pytest
import networkx as nx
import numpy as np

from src.smallworld import networks as H
from src.smallworld import networks_nx as O


def _edge_set(G: nx.Graph) -> set:
    """Undirected edge set as frozensets, so orientation does not matter."""
    return {frozenset(e) for e in G.edges()}


def _mean_degree(G: nx.Graph) -> float:
    return 2 * G.number_of_edges() / G.number_of_nodes()


# ------------ Ring builder ------------

def test_ring_node_count():
    G = H.build_ring(20, 4)
    assert G.number_of_nodes() == 20

def test_ring_edge_count():
    """A k-regular ring on N nodes has exactly N*k/2 edges."""
    G = H.build_ring(20, 4)
    assert G.number_of_edges() == 20 * 4 // 2

def test_ring_is_k_regular():
    """Every node connects to k/2 neighbours on each side, so degree == k."""
    G = H.build_ring(20, 4)
    assert all(d == 4 for _, d in G.degree())

def test_ring_no_self_loops():
    G = H.build_ring(20, 4)
    assert nx.number_of_selfloops(G) == 0

def test_ring_is_deterministic():
    """The ring lattice is seed-independent; two builds must be identical."""
    assert _edge_set(H.build_ring(30, 6)) == _edge_set(H.build_ring(30, 6, seed=99))


# ------------ Erdős-Rényi builder ------------

def test_er_node_count():
    G = H.build_er(50, 6, seed=0)
    assert G.number_of_nodes() == 50

def test_er_reproducible_with_seed():
    assert _edge_set(H.build_er(50, 6, seed=7)) == _edge_set(H.build_er(50, 6, seed=7))

def test_er_no_self_loops():
    G = H.build_er(50, 6, seed=0)
    assert nx.number_of_selfloops(G) == 0

def test_er_expected_degree_matches_k():
    """With p = k/(N-1) the expected mean degree is k; check it statistically."""
    degrees = [_mean_degree(H.build_er(400, 8, seed=s)) for s in range(20)]
    assert np.mean(degrees) == pytest.approx(8.0, abs=0.5)

def test_er_allows_odd_k():
    """ER only requires 0 < k < N (no even-k constraint), unlike the ring."""
    G = H.build_er(50, 5, seed=0)  # must not raise
    assert G.number_of_nodes() == 50


# ------------ Watts-Strogatz builder ------------

def test_ws_node_count():
    G = H.build_ws(60, 6, 0.1, seed=1)
    assert G.number_of_nodes() == 60

def test_ws_preserves_edge_count():
    """Rewiring removes and re-adds one edge at a time, so |E| = N*k/2 for any β."""
    for beta in [0.0, 0.1, 0.5, 1.0]:
        G = H.build_ws(60, 6, beta, seed=1)
        assert G.number_of_edges() == 60 * 6 // 2

def test_ws_no_self_loops():
    G = H.build_ws(60, 6, 0.5, seed=1)
    assert nx.number_of_selfloops(G) == 0

def test_ws_beta_zero_is_ring():
    """β = 0 performs no rewiring, so the result is exactly the ring lattice."""
    assert _edge_set(H.build_ws(30, 4, 0.0, seed=1)) == _edge_set(H.build_ring(30, 4))

def test_ws_reproducible_with_seed():
    assert _edge_set(H.build_ws(40, 6, 0.3, seed=5)) == _edge_set(H.build_ws(40, 6, 0.3, seed=5))

def test_ws_connected_flag_returns_connected_graph():
    G = H.build_ws(40, 6, 0.05, seed=3, connected=True)
    assert nx.is_connected(G)


# ------------ Validation ------------

@pytest.mark.parametrize("builder", [H.build_ring, H.build_er])
def test_rejects_N_too_small(builder):
    with pytest.raises(ValueError):
        builder(1, 0)

@pytest.mark.parametrize("builder", [H.build_ring, H.build_er])
def test_rejects_k_out_of_range(builder):
    with pytest.raises(ValueError):
        builder(10, 10)  # k must be strictly < N

def test_ring_rejects_odd_k():
    with pytest.raises(ValueError):
        H.build_ring(10, 3)

def test_ws_rejects_odd_k():
    with pytest.raises(ValueError):
        H.build_ws(10, 3, 0.1)

@pytest.mark.parametrize("beta", [-0.1, 1.1])
def test_ws_rejects_beta_out_of_range(beta):
    with pytest.raises(ValueError):
        H.build_ws(10, 4, beta)


# ------------ build_all ------------

def test_build_all_returns_three_named_graphs():
    graphs = H.build_all(N=30, k=6, beta=0.1, seed=0)
    assert set(graphs) == {"ring", "er", "ws"}
    assert all(isinstance(G, nx.Graph) for G in graphs.values())


# ------------ Oracle equivalence ------------

def test_ring_matches_oracle_exactly():
    """The hand-built ring lattice must be identical to the NetworkX oracle."""
    for N, k in [(10, 4), (20, 6), (50, 2)]:
        assert _edge_set(H.build_ring(N, k)) == _edge_set(O.build_ring(N, k))

def test_ws_beta_zero_matches_oracle_ring():
    """WS with β = 0 (hand) equals the oracle ring lattice exactly."""
    assert _edge_set(H.build_ws(30, 4, 0.0)) == _edge_set(O.build_ring(30, 4))

def test_er_mean_degree_matches_oracle_statistically():
    """Hand-built and oracle ER share p = k/(N-1); mean degrees agree on average."""
    hand = np.mean([_mean_degree(H.build_er(300, 6, seed=s)) for s in range(15)])
    oracle = np.mean([_mean_degree(O.build_er(300, 6, seed=s)) for s in range(15)])
    assert hand == pytest.approx(oracle, abs=0.5)
    assert hand == pytest.approx(6.0, abs=0.5)

def test_ws_clustering_matches_oracle_statistically():
    """Hand and oracle WS produce statistically comparable clustering at fixed β."""
    hand = np.mean([nx.transitivity(H.build_ws(200, 8, 0.1, seed=s)) for s in range(10)])
    oracle = np.mean([nx.transitivity(O.build_ws(200, 8, 0.1, seed=s)) for s in range(10)])
    assert hand == pytest.approx(oracle, abs=0.1)
