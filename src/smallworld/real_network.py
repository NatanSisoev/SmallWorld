"""Real-network analysis: Facebook Social Circles (SNAP).

Loads the Facebook ego-network dataset and applies the small-world pipeline
to a real-world graph:

* `load_facebook` — download / load the SNAP edge-list.
* `smallworldness_sigma` — compute the σ small-worldness coefficient.
* `fit_ws` — find the WS(N, k, β) equivalent.
* `plot_fitting_curve` — visualise the β-fitting result.

Dataset: J. McAuley and J. Leskovec. Learning to Discover Social Circles
in Ego Networks. NIPS, 2012.
"""

from __future__ import annotations

import gzip
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from src.smallworld.networks import build_er, build_ring, build_ws

__all__ = [
    "load_facebook",
    "smallworldness_sigma",
    "fit_ws",
]

_SNAP_URL = "https://snap.stanford.edu/data/facebook_combined.txt.gz"
_DEFAULT_PATH = Path("data") / "facebook_combined.txt.gz"


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _sample_apl(G: nx.Graph, n_samples: int = 500, seed: int | None = None) -> float:
    """Average path length estimated from *n_samples* random BFS sources."""
    rng = np.random.default_rng(seed)
    nodes = list(G.nodes())
    sources = rng.choice(nodes, size=min(n_samples, len(nodes)), replace=False)
    total = 0.0
    count = 0
    for s in sources:
        lengths = nx.single_source_shortest_path_length(G, int(s))
        vals = [d for t, d in lengths.items() if t != s]
        total += sum(vals)
        count += len(vals)
    return total / count if count > 0 else 0.0


# ---------------------------------------------------------------------------
# Load dataset
# ---------------------------------------------------------------------------

def load_facebook(path: str | Path | None = None) -> nx.Graph:
    """Load the Facebook Social Circles dataset (SNAP).

    If *path* is ``None`` and the file does not exist locally, downloads it
    from the SNAP repository and saves it to ``data/facebook_combined.txt.gz``.

    Parameters
    ----------
    path : str or Path, optional
        Local path to the ``.txt.gz`` edge-list file.  When ``None`` the
        default cache path ``data/facebook_combined.txt.gz`` is used.

    Returns
    -------
    networkx.Graph
        The largest connected component of the Facebook ego-network
        (4 039 nodes, 88 234 edges).
    """
    if path is None:
        path = _DEFAULT_PATH
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Downloading Facebook dataset from SNAP ...")
            urllib.request.urlretrieve(_SNAP_URL, path)
            print(f"  saved to {path}")

    path = Path(path)
    G = nx.Graph()
    with gzip.open(path, "rt") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            u, v = line.split()
            G.add_edge(int(u), int(v))

    lcc = max(nx.connected_components(G), key=len)
    return G.subgraph(lcc).copy()


# ---------------------------------------------------------------------------
# Smallworldness σ
# ---------------------------------------------------------------------------

def smallworldness_sigma(
    G: nx.Graph,
    n_random: int = 100,
    seed: int | None = 42,
    n_apl_samples: int = 500,
) -> dict:
    r"""Compute the σ small-worldness coefficient for *G*.

    $$\sigma = \frac{C_{\text{real}} / C_{\text{rand}}}{L_{\text{real}} / L_{\text{rand}}}$$

    $C_{\text{rand}}$ and $L_{\text{rand}}$ are averages over
    *n_random* Erdős–Rényi graphs with the same *N* and edge probability
    $p = 2|E| / (N(N-1))$.

    $L$ is estimated by BFS from *n_apl_samples* random source nodes
    (sampling is necessary for large graphs where all-pairs shortest paths
    would be too slow).

    Parameters
    ----------
    G : networkx.Graph
        Input graph.  Should be connected.
    n_random : int, default 100
        Number of random reference graphs.
    seed : int, optional
        Random seed for reproducibility.
    n_apl_samples : int, default 500
        BFS source nodes used to estimate L.  Reduce to 100–200 for faster
        builds; the estimate stays accurate for large connected graphs.

    Returns
    -------
    dict
        Keys: ``C_real``, ``L_real``, ``C_rand``, ``L_rand``, ``sigma``.
        σ > 1 indicates small-world behaviour.
    """
    N = G.number_of_nodes()
    M = G.number_of_edges()
    p = 2 * M / (N * (N - 1))

    C_real = float(nx.average_clustering(G))
    L_real = _sample_apl(G, n_samples=n_apl_samples, seed=seed)

    rng = np.random.default_rng(seed)
    C_rands, L_rands = [], []
    for _ in range(n_random):
        s = int(rng.integers(0, 2**31))
        G_rand = nx.erdos_renyi_graph(N, p, seed=s)
        if not nx.is_connected(G_rand):
            lcc = max(nx.connected_components(G_rand), key=len)
            G_rand = G_rand.subgraph(lcc).copy()
        C_rands.append(float(nx.average_clustering(G_rand)))
        L_rands.append(_sample_apl(G_rand, n_samples=n_apl_samples, seed=s))

    C_rand = float(np.mean(C_rands))
    L_rand = float(np.mean(L_rands))
    sigma  = (C_real / C_rand) / (L_real / L_rand)

    return {
        "C_real": C_real,
        "L_real": L_real,
        "C_rand": C_rand,
        "L_rand": L_rand,
        "sigma":  sigma,
    }


# ---------------------------------------------------------------------------
# β-fitting
# ---------------------------------------------------------------------------

def fit_ws(
    G: nx.Graph,
    beta_values: list | None = None,
    n_reps: int = 5,
    n_apl_samples: int = 500,
    verbose: bool = True,
) -> dict:
    """Find the WS(N, k, β) model that best replicates *G*.

    Algorithm
    ---------
    1. Derive N and k from *G* (k rounded to nearest even integer).
    2. Compute ring and ER baselines to define the normalisation range.
    3. For each β in *beta_values* average (L, C) over *n_reps* realisations.
    4. Normalise L and C to [0, 1] using [L_rand, L_ring] and [C_rand, C_ring].
    5. Return β* = argmin Euclidean distance to the real-network point.

    Parameters
    ----------
    G : networkx.Graph
        Real network to fit.
    beta_values : list of float, optional
        β values to sweep.  Defaults to 30 log-spaced values in [10⁻³, 1].
    n_reps : int, default 5
        WS realisations averaged per β.  3 is enough for documentation builds.
    n_apl_samples : int, default 500
        BFS source nodes used to estimate L per graph.  100 is fast and
        accurate enough for fitting on large connected graphs.
    verbose : bool, default True
        Print progress for each β.

    Returns
    -------
    dict
        Keys: ``N``, ``k``, ``beta_optimal``, ``L_real``, ``C_real``,
        ``L_ws_fitted``, ``C_ws_fitted``, ``distance``, ``beta_curve``
        (list of ``(beta, L_norm, C_norm)`` tuples), plus normalised
        reference values ``L_real_norm``, ``C_real_norm``.
    """
    if beta_values is None:
        beta_values = list(np.logspace(-3, 0, 30))

    N       = G.number_of_nodes()
    degrees = [d for _, d in G.degree()]
    k       = int(round(float(np.mean(degrees))))
    if k % 2 != 0:
        k += 1

    if verbose:
        print(f"fit_ws: N={N}, k={k}, {len(beta_values)} β values, "
              f"{n_reps} reps, {n_apl_samples} APL samples …")

    C_real = float(nx.average_clustering(G))
    L_real = _sample_apl(G, n_samples=n_apl_samples, seed=42)

    # Ring baseline
    G_ring = build_ring(N, k)
    C_ring = float(nx.average_clustering(G_ring))
    L_ring = _sample_apl(G_ring, n_samples=n_apl_samples, seed=42)

    # ER baseline
    G_er = build_er(N, k, seed=42)
    if not nx.is_connected(G_er):
        lcc  = max(nx.connected_components(G_er), key=len)
        G_er = G_er.subgraph(lcc).copy()
    C_er = float(nx.average_clustering(G_er))
    L_er = _sample_apl(G_er, n_samples=n_apl_samples, seed=42)

    L_range = L_ring - L_er
    C_range = C_ring - C_er

    def _norm_L(L: float) -> float:
        return (L - L_er) / L_range if L_range > 0 else 0.0

    def _norm_C(C: float) -> float:
        return (C - C_er) / C_range if C_range > 0 else 0.0

    L_real_norm = _norm_L(L_real)
    C_real_norm = _norm_C(C_real)

    beta_curve: list[tuple[float, float, float]] = []
    best_beta  = beta_values[0]
    best_dist  = float("inf")
    best_L_ws  = L_real
    best_C_ws  = C_real

    for beta in beta_values:
        L_ws_vals, C_ws_vals = [], []
        for rep in range(n_reps):
            Gw = build_ws(N, k, beta, seed=rep)
            L_ws_vals.append(_sample_apl(Gw, n_samples=n_apl_samples, seed=rep))
            C_ws_vals.append(float(nx.average_clustering(Gw)))
        L_ws     = float(np.mean(L_ws_vals))
        C_ws     = float(np.mean(C_ws_vals))
        L_ws_n   = _norm_L(L_ws)
        C_ws_n   = _norm_C(C_ws)
        dist     = float(np.sqrt((L_ws_n - L_real_norm) ** 2 + (C_ws_n - C_real_norm) ** 2))
        beta_curve.append((float(beta), L_ws_n, C_ws_n))
        if dist < best_dist:
            best_dist = dist
            best_beta = float(beta)
            best_L_ws = L_ws
            best_C_ws = C_ws
        if verbose:
            print(f"  β={beta:.5f}  L={L_ws:.3f}  C={C_ws:.3f}  dist={dist:.4f}")

    return {
        "N":            N,
        "k":            k,
        "beta_optimal": best_beta,
        "L_real":       L_real,
        "C_real":       C_real,
        "L_ws_fitted":  best_L_ws,
        "C_ws_fitted":  best_C_ws,
        "distance":     best_dist,
        "beta_curve":   [list(t) for t in beta_curve],
        "L_real_norm":  L_real_norm,
        "C_real_norm":  C_real_norm,
    }


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

def plot_fitting_curve(
    fit_result: dict,
    sigma_result: dict,
    save_path: str | Path | None = None,
):
    """Plot the β-fitting result in two subplots.

    Subplot 1 — normalised (L, C) space
        WS β-curve from ring (β → 0) to random (β → 1), with the real
        network point and the best-fit β* marked.

    Subplot 2 — σ breakdown
        Bars for C_real/C_rand and L_real/L_rand with the σ value highlighted.

    Parameters
    ----------
    fit_result : dict
        Output of `fit_ws`.
    sigma_result : dict
        Output of `smallworldness_sigma`.
    save_path : str or Path, optional
        If given, saves the figure at 150 dpi.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing both subplots.
    axes : tuple of matplotlib.axes.Axes
        The two subplot axes ``(ax1, ax2)``.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # --- subplot 1: normalised (L_norm, C_norm) ---
    betas  = [t[0] for t in fit_result["beta_curve"]]
    L_norms = [t[1] for t in fit_result["beta_curve"]]
    C_norms = [t[2] for t in fit_result["beta_curve"]]

    ax1.plot(L_norms, C_norms, "b-o", markersize=4, linewidth=1.2,
             label="WS β-curve", zorder=2)

    ax1.scatter(
        fit_result["L_real_norm"], fit_result["C_real_norm"],
        color="red", s=140, zorder=5, label="Facebook (real)", marker="D",
    )

    best_idx = next(
        i for i, t in enumerate(fit_result["beta_curve"])
        if t[0] == fit_result["beta_optimal"]
    )
    ax1.scatter(
        fit_result["beta_curve"][best_idx][1],
        fit_result["beta_curve"][best_idx][2],
        color="#4CAF50", s=180, marker="*", zorder=5,
        label=f"β* = {fit_result['beta_optimal']:.4f}",
    )

    ax1.set_xlabel("L (normalitzat)  →  0 = ER, 1 = ring", fontsize=10)
    ax1.set_ylabel("C (normalitzat)  →  0 = ER, 1 = ring", fontsize=10)
    ax1.set_title("Espai normalitzat (L, C)", fontsize=13, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.3)

    # --- subplot 2: σ breakdown ---
    ratios = [
        sigma_result["C_real"] / sigma_result["C_rand"],
        sigma_result["L_real"] / sigma_result["L_rand"],
    ]
    labels = ["C_real / C_rand", "L_real / L_rand"]
    colors = ["#4CAF50", "#2196F3"]
    bars = ax2.bar(labels, ratios, color=colors, edgecolor="black", width=0.4)
    ax2.axhline(1.0, color="black", linestyle="--", linewidth=1, alpha=0.6,
                label="referència = 1")
    for bar, val in zip(bars, ratios):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{val:.3f}",
            ha="center", va="bottom", fontsize=11, fontweight="bold",
        )
    ax2.set_ylabel("Ràtio", fontsize=11)
    ax2.set_title(
        f"Smallworldness  σ = {sigma_result['sigma']:.2f}",
        fontsize=13, fontweight="bold",
    )
    ax2.legend(fontsize=9)
    ax2.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    if save_path is not None:
        fig.savefig(Path(save_path), dpi=150, bbox_inches="tight")
    return fig, (ax1, ax2)
