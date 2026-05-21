"""Tests for simulation file"""

import pytest
import networkx as nx
import numpy as np

from src.smallworld.networks import build_all
from src.smallworld.simulation import (
    random_walk_step,
    random_walk,
    build_transition_matrix,
    mixing_time,
    cover_time,
)


@pytest.fixture(scope="module")
def ring():
    """Small ring graph shared across tests."""
    return build_all(N=20, k=4, seed=42)["ring"]


@pytest.fixture
def k5():
    """Complete graph K5 — useful for analytically known values."""
    return nx.complete_graph(5)


# ------------ Build Transition Matrix tests ------------

def test_shape(ring: nx.Graph):
    P, dim = build_transition_matrix(ring)
    assert P.shape == (dim, dim)
    assert dim == ring.number_of_nodes()

def test_columns_sum_to_one(ring: nx.Graph):
    P, _ = build_transition_matrix(ring)
    np.testing.assert_allclose(P.sum(axis=0), 1.0, atol=1e-10)

def test_nonnegative(ring: nx.Graph):
    P, _ = build_transition_matrix(ring)
    assert (P >= 0).all()

def test_k5_uniform_entries(k5):
    """In K5 each off-diagonal entry must equal 1/4."""
    P, dim = build_transition_matrix(k5)
    expected = 1 / (dim - 1)
    for i in range(dim):
        for j in range(dim):
            if i == j:
                assert P[i, j] == pytest.approx(0.0)
            else:
                assert P[i, j] == pytest.approx(expected)


# ------------ Random Walk Step ------------

def test_next_is_neighbour(ring: nx.Graph):
    np.random.seed(0)
    node = list(ring.nodes)[0]
    assert random_walk_step(ring, node) in ring.neighbors(node)

def test_reproducible_with_seed(ring: nx.Graph):
    node = list(ring.nodes)[0]
    np.random.seed(7)
    a = random_walk_step(ring, node)
    np.random.seed(7)
    b = random_walk_step(ring, node)
    assert a == b


# ------------ Random Wallk ------------

def test_trace_length(ring: nx.Graph):
    np.random.seed(0)
    start = list(ring.nodes)[0]
    assert len(random_walk(ring, start=start, n_steps=10)) == 10

def test_zero_steps(ring):
    start = list(ring.nodes)[0]
    assert random_walk(ring, start=start, n_steps=0) == []

def test_each_step_is_a_neighbour(ring: nx.Graph):
    """Every consecutive pair in the trace must be connected by an edge."""
    np.random.seed(0)
    start = list(ring.nodes)[0]
    trace = random_walk(ring, start=start, n_steps=30)
    prev = start
    for node in trace:
        assert node in ring.neighbors(prev)
        prev = node


# ------------ Mixing Time ------------

def test_return_types(ring: nx.Graph):
    out_dic, time_avg = mixing_time(ring, n_simulations=5, seed=42)
    assert isinstance(out_dic, dict)
    assert isinstance(time_avg, float)

def test_all_simulations_present(ring: nx.Graph):
    n_sim = 5
    out_dic, _ = mixing_time(ring, n_simulations=n_sim, seed=42)
    assert len(out_dic) == n_sim

def test_simulation_keys(ring: nx.Graph):
    out_dic, _ = mixing_time(ring, n_simulations=3, seed=42)
    for entry in out_dic.values():
        assert "iters" in entry
        assert "distribution" in entry

def test_stationary_distribution_sums_to_one(ring: nx.Graph):
    out_dic, _ = mixing_time(ring, n_simulations=3, seed=42)
    for entry in out_dic.values():
        np.testing.assert_allclose(entry["distribution"].sum(), 1.0, atol=1e-5)

def test_reproducible_with_seed(ring):
    _, t1 = mixing_time(ring, n_simulations=5, seed=99)
    _, t2 = mixing_time(ring, n_simulations=5, seed=99)
    assert t1 == pytest.approx(t2)
    
# ------------ Cover Time ------------

def test_cover_time_return_types(ring: nx.Graph):
    steps, avg = cover_time(ring, n_simulations=5, seed=42)
    assert isinstance(steps, list)
    assert isinstance(avg, (float, np.floating))

def test_cover_time_num_simulations(ring: nx.Graph):
    n_sim = 5
    steps, _ = cover_time(ring, n_simulations=n_sim, seed=42)
    assert len(steps) == n_sim

def test_cover_time_steps_nonnegative(ring: nx.Graph):
    steps, _ = cover_time(ring, n_simulations=5, seed=42)
    assert all(s >= 0 for s in steps)

def test_cover_time_avg_consistent(ring: nx.Graph):
    """Average must match the mean of the returned steps list."""
    steps, avg = cover_time(ring, n_simulations=10, seed=42)
    assert avg == pytest.approx(np.mean(steps))

def test_cover_time_reproducible_with_seed(ring: nx.Graph):
    _, avg1 = cover_time(ring, n_simulations=5, seed=7)
    _, avg2 = cover_time(ring, n_simulations=5, seed=7)
    assert avg1 == pytest.approx(avg2)

def test_cover_time_max_iter_returns_inf(ring: nx.Graph):
    """A tiny max_iter forces non-convergence → average must be np.inf."""
    _, avg = cover_time(ring, n_simulations=3, seed=42, max_iter=1)
    assert avg == np.inf