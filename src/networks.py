"""Network constructors for the small-world study.

This module wraps :mod:`networkx` builders for the three reference
network models used throughout the project:

* :func:`build_ring` — regular ring lattice (Watts-Strogatz with β = 0).
* :func:`build_er`   — Erdős-Rényi G(N, p) with expected degree ``k``.
* :func:`build_ws`   — Watts-Strogatz with rewiring probability ``β``.

All builders accept an optional ``seed`` for reproducibility and return
an undirected, unweighted :class:`networkx.Graph` on ``N`` nodes labelled
``0, 1, ..., N - 1``.
"""

from __future__ import annotations

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
        The ring lattice ``C(N, k)``.
    """
    _validate_ring_params(N, k)
    return nx.watts_strogatz_graph(N, k, p=0.0, seed=seed)


def build_er(N: int, k: int, *, seed: int | None = None) -> nx.Graph:
    """Build an Erdős-Rényi G(N, p) with expected average degree ``k``.

    The edge probability is set to ``p = k / (N - 1)`` so that the
    expected degree of every node equals ``k``, matching the regular and
    Watts-Strogatz networks for fair comparison.

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
    """
    _validate_Nk(N, k)
    p = k / (N - 1)
    return nx.erdos_renyi_graph(N, p, seed=seed)


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

    Starts from the ring lattice ``C(N, k)`` and rewires each edge with
    probability ``beta`` to a uniformly random endpoint, avoiding
    self-loops and duplicate edges.

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
        A Watts-Strogatz graph WS(N, k, β).
    """
    _validate_ring_params(N, k)
    if not 0.0 <= beta <= 1.0:
        raise ValueError(f"beta must be in [0, 1] (got {beta})")

    if connected:
        return nx.connected_watts_strogatz_graph(
            N, k, p=beta, tries=tries, seed=seed
        )
    return nx.watts_strogatz_graph(N, k, p=beta, seed=seed)


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
        Number of nodes.
    k : int
        Average degree (exact for the ring and WS, expected for ER).
    beta : float, default 0.1
        Rewiring probability for the Watts-Strogatz graph.
    seed : int, default 0
        Random seed shared across builders.

    Returns
    -------
    dict[str, networkx.Graph]
        Mapping with keys ``"ring"``, ``"er"`` and ``"ws"``.
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
