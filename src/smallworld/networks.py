"""Hand-built network constructors for the small-world study.

This module implements the three reference network models from scratch:
`networkx.Graph` is used only as the underlying container so that
visualisation and standard graph utilities keep working; every edge is
added by our own code. A reference implementation that delegates to the
``networkx`` constructors is preserved in `src.smallworld.networks_nx`
for equivalence testing.

* `build_ring` — regular ring lattice (deterministic).
* `build_er`   — Erdős-Rényi G(N, p) with expected degree ``k``.
* `build_ws`   — Watts-Strogatz with rewiring probability ``β``.

All builders accept an optional ``seed`` for reproducibility and return
an undirected, unweighted `networkx.Graph` on ``N`` nodes labelled
``0, 1, ..., N - 1``.
"""

from __future__ import annotations

import random

import networkx as nx

__all__ = ["build_ring", "build_er", "build_ws", "build_all"]


def build_ring(N: int, k: int, *, seed: int | None = None) -> nx.Graph:
    """Build a regular ring lattice with ``N`` nodes and degree ``k``.

    Each node is connected to its ``k / 2`` nearest neighbours on each
    side of the ring, so every node has degree exactly ``k``.

    Parameters
    ----------
    N : int
        Number of nodes. Must satisfy ``N >= 2``.
    k : int
        Degree of every node. Must be even and satisfy ``0 < k < N``.
    seed : int, optional
        Unused (the ring lattice is deterministic); kept so all builders
        share a uniform signature.

    Returns
    -------
    networkx.Graph
        The ring lattice ``C(N, k)`` — a ``k``-regular undirected graph.

    Raises
    ------
    ValueError
        If ``N < 2``, ``k`` is not even, or ``k`` does not satisfy
        ``0 < k < N``.
    """
    _validate_ring_params(N, k)
    G = nx.Graph()
    G.add_nodes_from(range(N))
    half = k // 2
    for i in range(N):
        for j in range(1, half + 1):
            G.add_edge(i, (i + j) % N)
    return G


def build_er(N: int, k: int, *, seed: int | None = None) -> nx.Graph:
    """Build an Erdős-Rényi G(N, p) with expected average degree ``k``.

    The edge probability is ``p = k / (N - 1)`` so that the expected
    degree of every node equals ``k``, matching the regular and
    Watts-Strogatz networks for fair comparison. Each unordered pair
    ``{i, j}`` with ``i < j`` is sampled independently with probability
    ``p``.

    Notes
    -----
    The convention ``p = k / (N - 1)`` (rather than ``k / N``) matches
    `networkx.erdos_renyi_graph`'s exact expected-degree relation and
    gives a slightly better approximation for small ``N``.

    Parameters
    ----------
    N : int
        Number of nodes. Must satisfy ``N >= 2``.
    k : int
        Target average degree. Must satisfy ``0 < k < N``.
    seed : int, optional
        Random seed for reproducibility.

    Returns
    -------
    networkx.Graph
        A realisation of G(N, k / (N - 1)). May be disconnected for
        small ``k``; callers that need a connected graph should restrict
        to the largest connected component.

    Raises
    ------
    ValueError
        If ``N < 2`` or ``k`` does not satisfy ``0 < k < N``.
    """
    _validate_Nk(N, k)
    rng = random.Random(seed)
    p = k / (N - 1)
    G = nx.Graph()
    G.add_nodes_from(range(N))
    for i in range(N):
        for j in range(i + 1, N):
            if rng.random() < p:
                G.add_edge(i, j)
    return G


def build_ws(
    N: int,
    k: int,
    beta: float,
    *,
    seed: int | None = None,
    connected: bool = False,
    tries: int = 100,
) -> nx.Graph:
    """Build a Watts-Strogatz small-world graph.

    Starts from the ring lattice ``C(N, k)`` and iterates its edges in
    the canonical Watts-Strogatz order — for each offset ``j = 1..k/2``,
    visit every node ``u = 0..N-1`` and consider the edge ``(u, u+j)``
    — rewiring it with probability ``beta`` to a uniformly random
    non-neighbour ``≠ u``. Self-loops and duplicate edges are forbidden;
    if no valid target exists the edge is left untouched.

    Parameters
    ----------
    N : int
        Number of nodes. Must satisfy ``N >= 2``.
    k : int
        Initial degree of every node. Must be even and satisfy
        ``0 < k < N``.
    beta : float
        Rewiring probability, in ``[0, 1]``.
    seed : int, optional
        Random seed for reproducibility.
    connected : bool, default False
        If True, retry construction up to ``tries`` times until the
        result is connected. Useful for very small ``beta``, where the
        plain rewiring may leave isolated components.
    tries : int, default 100
        Maximum number of retries used when ``connected=True``.

    Returns
    -------
    networkx.Graph
        A Watts-Strogatz graph WS(N, k, β). May be disconnected for
        very small ``beta``; use ``connected=True`` to guarantee
        connectivity.

    Raises
    ------
    ValueError
        If ``N < 2``, ``k`` is not even, ``k`` does not satisfy
        ``0 < k < N``, or ``beta`` is outside ``[0, 1]``.
    RuntimeError
        If ``connected=True`` and no connected graph is produced within
        ``tries`` attempts.
    """
    _validate_ring_params(N, k)
    if not 0.0 <= beta <= 1.0:
        raise ValueError(f"beta must be in [0, 1] (got {beta})")

    if connected:
        for attempt in range(tries):
            attempt_seed = seed if seed is None else seed + attempt
            G = _build_ws_once(N, k, beta, seed=attempt_seed)
            if nx.is_connected(G):
                return G
        raise RuntimeError(
            f"Failed to produce a connected WS graph after {tries} tries; "
            f"try a larger beta or a larger k."
        )
    return _build_ws_once(N, k, beta, seed=seed)


def _build_ws_once(
    N: int, k: int, beta: float, *, seed: int | None
) -> nx.Graph:
    """One Watts-Strogatz rewiring pass (no connectivity retry)."""
    rng = random.Random(seed)
    G = build_ring(N, k)
    half = k // 2
    for j in range(1, half + 1):
        for u in range(N):
            v = (u + j) % N
            if rng.random() < beta:
                candidates = [
                    w for w in range(N) if w != u and not G.has_edge(u, w)
                ]
                if not candidates:
                    continue
                new_v = rng.choice(candidates)
                G.remove_edge(u, v)
                G.add_edge(u, new_v)
    return G


def build_all(
    N: int,
    k: int,
    beta: float = 0.1,
    *,
    seed: int | None = 0,
) -> dict[str, nx.Graph]:
    """Build the three reference networks at the same ``N`` and ``k``.

    Convenience wrapper used throughout the notebooks. The same ``seed``
    is forwarded to each builder so results are reproducible.

    Parameters
    ----------
    N : int
        Number of nodes. Must satisfy ``N >= 2``.
    k : int
        Average degree — exact for the ring and WS, expected for ER.
        Must be even and satisfy ``0 < k < N``.
    beta : float, default 0.1
        Rewiring probability for the Watts-Strogatz graph, in ``[0, 1]``.
    seed : int, default 0
        Random seed shared across all three builders.

    Returns
    -------
    dict[str, networkx.Graph]
        Mapping with keys ``"ring"``, ``"er"``, and ``"ws"``.

    Raises
    ------
    ValueError
        Propagated from the individual builders if any parameter is
        out of range.
    """
    return {
        "ring": build_ring(N, k, seed=seed),
        "er": build_er(N, k, seed=seed),
        "ws": build_ws(N, k, beta, seed=seed),
    }


def _validate_Nk(N: int, k: int) -> None:
    """Validate ``(N, k)`` for any constructor."""
    if N < 2:
        raise ValueError(f"N must be >= 2 (got {N})")
    if not 0 < k < N:
        raise ValueError(f"k must satisfy 0 < k < N (got k={k}, N={N})")


def _validate_ring_params(N: int, k: int) -> None:
    """Validate ``(N, k)`` for ring-based constructors (ring, WS)."""
    _validate_Nk(N, k)
    if k % 2 != 0:
        raise ValueError(f"k must be even for the ring lattice (got {k})")
