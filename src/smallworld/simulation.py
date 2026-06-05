r"""Random-walk simulation on small-world networks.

Provides hand-written implementations of the three core random-walk
quantities studied in the course:

* `random_walk_step` / `random_walk` — basic walk primitives.
* `stationary_distribution` — exact $\pi(v) = \deg(v) / 2|E|$.
* `build_transition_matrix` — column-stochastic matrix P.
* `cover_time` — Monte-Carlo cover-time estimate.
* `mixing_time` — matrix-iteration mixing-time estimate.

All stochastic functions accept a ``seed`` argument (or a
`numpy.random.Generator`) for reproducibility.

Plotting helpers (`plot_cover_time`,
`plot_mixing_time_distribution`) live in `src.smallworld.plotting`.
"""

from __future__ import annotations

import warnings

import networkx as nx
import numpy as np
import numpy.typing as npt

__all__ = [
    "random_walk_step",
    "random_walk",
    "stationary_distribution",
    "build_transition_matrix",
    "cover_time",
    "mixing_time",
]

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

_RNG = np.random.Generator


# ---------------------------------------------------------------------------
# Walk primitives
# ---------------------------------------------------------------------------

def random_walk_step(
    G: nx.Graph,
    current_node: int,
    *,
    rng: _RNG | None = None,
) -> int:
    """Take a single random step from *current_node* to one of its neighbours.

    Parameters
    ----------
    G : networkx.Graph
        The graph on which to walk.
    current_node : int
        The node from which to step.
    rng : numpy.random.Generator, optional
        Random generator.  Falls back to ``numpy``'s global generator when
        ``None``.

    Returns
    -------
    int
        A neighbour of *current_node* chosen uniformly at random.

    Raises
    ------
    ValueError
        If *current_node* is isolated (no neighbours).
    """
    neighbors = list(G.neighbors(current_node))
    if not neighbors:
        raise ValueError(
            f"Node {current_node} is isolated; cannot take a random-walk step."
        )
    if rng is not None:
        return int(rng.choice(neighbors))
    return int(np.random.choice(neighbors))


def random_walk(
    G: nx.Graph,
    start: int,
    n_steps: int,
    *,
    rng: _RNG | int | None = None,
) -> list[int]:
    """Simulate a random walk of *n_steps* steps starting from *start*.

    Parameters
    ----------
    G : networkx.Graph
        The graph on which to walk.
    start : int
        Starting node.
    n_steps : int
        Number of steps to take.
    rng : Generator or int, optional
        Random generator or integer seed.  A fresh generator is created when
        an ``int`` is passed; the global generator is used when ``None``.

    Returns
    -------
    list[int]
        Sequence of nodes visited *after* the start (length ``n_steps``).

    Raises
    ------
    ValueError
        If any node reached during the walk is isolated (no neighbours).
        Use a connected graph to avoid this.
    """
    if isinstance(rng, (int, np.integer)):
        rng = np.random.default_rng(int(rng))
    current = start
    trace: list[int] = []
    for _ in range(n_steps):
        current = random_walk_step(G, current, rng=rng)
        trace.append(current)
    return trace


# ---------------------------------------------------------------------------
# Stationary distribution
# ---------------------------------------------------------------------------

def stationary_distribution(G: nx.Graph) -> npt.NDArray[np.float64]:
    r"""Compute the exact stationary distribution for a random walk on *G*.

    For any undirected graph the stationary distribution is:

    $$\pi(v) = \frac{\deg(v)}{2|E|}$$

    For a *k*-regular graph this reduces to the uniform distribution:
    $\pi(v) = 1/N$.

    Notes
    -----
    If the graph has no edges at all (all nodes isolated), the function
    returns a uniform distribution over all nodes as a safe fallback.
    Nodes are assumed to be labelled ``0, 1, ..., N-1`` in sorted order.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, unweighted graph on *N* nodes.

    Returns
    -------
    numpy.ndarray, shape (N,)
        Probability vector $\pi$ indexed by node label, summing to 1.
    """
    degrees = np.array([G.degree(v) for v in sorted(G.nodes())], dtype=float)
    total = degrees.sum()
    if total == 0:
        return np.ones(len(degrees)) / len(degrees)
    return degrees / total


# ---------------------------------------------------------------------------
# Transition matrix
# ---------------------------------------------------------------------------

def build_transition_matrix(
    G: nx.Graph,
) -> tuple[npt.NDArray[np.float64], int]:
    r"""Build the column-stochastic transition matrix for a random walk on *G*.

    Entry $P_{ij}$ is the probability of moving **from** node $j$
    **to** node $i$ in one step:

    $$P_{ij} = \begin{cases}
    1/\deg(j) & (i,j) \in E \\
    0         & \text{otherwise}
    \end{cases}$$

    For a *k*-regular graph the stationary distribution is uniform:
    $\pi(v) = 1/N$.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, unweighted graph on *N* nodes labelled ``0 … N-1``.

    Returns
    -------
    P : numpy.ndarray, shape (N, N)
        Column-stochastic transition matrix.
    N : int
        Number of nodes.
    """
    n = G.number_of_nodes()
    P = np.zeros((n, n), dtype=float)
    for node in G.nodes():
        neighbors = list(G.neighbors(node))
        deg = len(neighbors)
        if deg > 0:
            P[neighbors, node] = 1.0 / deg
    return P, n


# ---------------------------------------------------------------------------
# Cover time
# ---------------------------------------------------------------------------

def cover_time(
    G: nx.Graph,
    n_simulations: int,
    seed: int | None = None,
    max_iter: int = 100_000,
) -> tuple[list[int], float]:
    r"""Estimate the cover time of *G* by Monte-Carlo simulation.

    The **cover time** $C(G)$ is the expected number of steps a random
    walk needs to visit every node at least once. This function approximates
    it by averaging over many independent simulations, each started from a
    uniformly random non-isolated node.

    Empirical scaling laws:

    | Graph | Scaling |
    |-------|---------|
    | Ring lattice | $\Theta(N^2)$ |
    | ER / WS | $\Theta(N \log N)$ |

    Parameters
    ----------
    G : networkx.Graph
        Graph to simulate on.  Isolated nodes are excluded automatically.
    n_simulations : int
        Number of independent random walks to run.
    seed : int, optional
        Seed for the random-number generator.
    max_iter : int, default 100 000
        Hard step limit per simulation.  Walks that reach this limit are
        counted as ``max_iter`` steps and a `UserWarning` is raised.

    Returns
    -------
    num_steps : list[int]
        Number of steps taken in each simulation.
    avg : float
        Mean cover time across all simulations.
    """
    rng = np.random.default_rng(seed)

    all_nodes = [n for n in G.nodes() if G.degree(n) > 0]
    isolated  = G.number_of_nodes() - len(all_nodes)
    if isolated:
        warnings.warn(
            f"{isolated} isolated node(s) excluded from cover-time simulation.",
            stacklevel=2,
        )
    if not all_nodes:
        return [], np.inf  # type: ignore[return-value]

    num_steps: list[int] = []
    for _ in range(n_simulations):
        start     = int(rng.choice(all_nodes))
        to_visit  = set(all_nodes) - {start}
        current   = start

        for step in range(max_iter):
            current = int(rng.choice(list(G.neighbors(current))))
            to_visit.discard(current)
            if not to_visit:
                num_steps.append(step + 1)
                break
        else:
            warnings.warn(
                f"A simulation reached max_iter={max_iter:,} without visiting all nodes; "
                f"recording max_iter as its cover time.",
                stacklevel=2,
            )
            num_steps.append(max_iter)

    return num_steps, float(np.mean(num_steps))


# ---------------------------------------------------------------------------
# Mixing time
# ---------------------------------------------------------------------------

def mixing_time(
    G: nx.Graph,
    n_simulations: int,
    seed: int | None = None,
    tol: float = 1e-5,
    max_iter: int = 10_000,
) -> tuple[dict[int, dict], float]:
    r"""Estimate the mixing time of *G* by iterated matrix–vector products.

    The **mixing time** measures how many steps a random walk needs before its
    distribution converges (within tolerance *tol*) to the stationary
    distribution $\pi(v) = \deg(v) / 2|E|$.

    Convergence is tracked via total-variation distance to the stationary
    distribution:

    $$t_{\mathrm{mix}} = \min\bigl\{t : \tfrac12\|\mathbf{p}_t - \pi\|_1 < \varepsilon \bigr\}$$

    Parameters
    ----------
    G : networkx.Graph
        Graph whose mixing time is to be estimated.
    n_simulations : int
        Number of independent runs (each uses a fresh random $\mathbf{p}_0$).
    seed : int, optional
        Seed for the random-number generator.
    tol : float, default 1e-5
        Convergence tolerance $\varepsilon$.
    max_iter : int, default 10 000
        Maximum number of matrix–vector multiplications per simulation.

    Returns
    -------
    results : dict[int, dict]
        Keyed by simulation index ``0 … n_simulations-1``.  Each entry has:

        - ``"iters"`` — iterations until convergence (``max_iter`` if not
          converged).
        - ``"distribution"`` — final probability vector, shape ``(N,)``.
    avg_iters : float
        Average number of iterations across all simulations.
    """
    rng = np.random.default_rng(seed)
    P, n = build_transition_matrix(G)
    pi = stationary_distribution(G)

    results: dict[int, dict] = {}
    for sim in range(n_simulations):
        # Random initial distribution, normalised to sum to 1
        p = rng.random(n)
        p /= p.sum()

        for t in range(1, max_iter + 1):
            p = P @ p
            tv_distance = 0.5 * float(np.sum(np.abs(p - pi)))
            if tv_distance < tol:
                results[sim] = {
                    "iters": t,
                    "distribution": p,
                    "tv_distance": tv_distance,
                }
                break
        else:
            warnings.warn(
                f"Simulation {sim} did not converge within {max_iter} iterations.",
                stacklevel=2,
            )
            tv_distance = 0.5 * float(np.sum(np.abs(p - pi)))
            results[sim] = {
                "iters": max_iter,
                "distribution": p,
                "tv_distance": tv_distance,
            }

    avg_iters = float(np.mean([results[s]["iters"] for s in results]))
    return results, avg_iters
