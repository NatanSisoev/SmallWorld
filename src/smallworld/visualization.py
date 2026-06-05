"""Interactive random-walk visualisation via vis.js.

Generates self-contained HTML pages that embed a vis.js graph together
with a walk-control panel.  The pages are designed to be served as
``<iframe>`` embeds inside the MkDocs documentation site.

HTML templates live in ``src/smallworld/templates/`` and use ``@@key@@``
placeholders.  Python fills them with `_render`.

The main entry points are:

* `build_walk_visualization` — HTML for one interactive walk.
* `save_walk_visualization` — write it to disk.
* `build_cover_time_visualization` — HTML for cover-time histogram.
* `save_cover_time_visualization` — write it to disk.
* `build_compare_times_visualization` — HTML for side-by-side comparison.
* `save_compare_times_visualization` — write it to disk.
* `build_metrics_analytics_visualization` — HTML for the L/C vs β analytics page.
* `save_metrics_analytics_visualization` — write it to disk.

Node colour convention
----------------------
* **green**  — start node (initial position).
* **red**    — current walker position.
* **orange** — already visited.
* **blue**   — not yet visited.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import networkx as nx

from src.smallworld.plotting import _layout

__all__ = [
    "build_walk_visualization",
    "save_walk_visualization",
    "build_cover_time_visualization",
    "save_cover_time_visualization",
    "build_compare_times_visualization",
    "save_compare_times_visualization",
    "build_metrics_analytics_visualization",
    "save_metrics_analytics_visualization",
    "compute_metrics_data",
    "build_metrics_analytics_from_data",
    "build_facebook_visualization",
    "save_facebook_visualization",
]

_TEMPLATES_DIR = Path(__file__).parent / "templates"


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------

def _render(template_name: str, **kwargs: object) -> str:
    """Load *template_name* from ``templates/`` and fill ``@@key@@`` slots.

    Parameters
    ----------
    template_name : str
        Filename inside ``src/smallworld/templates/`` (e.g. ``"walk.html"``).
    **kwargs
        Key-value pairs substituted for every ``@@key@@`` occurrence in the
        template.  Values are converted to ``str`` before substitution.

    Returns
    -------
    str
        The rendered HTML document.
    """
    text = (_TEMPLATES_DIR / template_name).read_text(encoding="utf-8")
    for key, value in kwargs.items():
        text = text.replace(f"@@{key}@@", str(value))
    return text


# ---------------------------------------------------------------------------
# Interactive walk visualisation
# ---------------------------------------------------------------------------

def build_walk_visualization(
    G: nx.Graph,
    *,
    start: int = 0,
    layout: str = "circular",
    height: str = "560px",
    seed: int = 42,
    scale: float = 350.0,
    title: str = "",
) -> str:
    """Generate a self-contained HTML page for interactive random-walk exploration.

    Parameters
    ----------
    G : networkx.Graph
        Graph to visualise.  Should be connected so the walker can reach
        every node.
    start : int, default 0
        Node where the walk begins.
    layout : {"circular", "spring"}, default ``"circular"``
        NetworkX layout used to position nodes initially.
    height : str, default ``"560px"``
        CSS height of the vis.js canvas.
    seed : int, default 42
        Random seed for the spring layout (ignored for circular).
    scale : float, default 350.0
        Scaling factor (pixels) passed to the layout function.
    title : str, default ``""``
        Optional heading rendered above the graph.

    Returns
    -------
    str
        A complete, UTF-8 HTML document.  Save it with
        `save_walk_visualization` or embed it in an ``<iframe>``.
    """
    pos = _layout(G, layout, seed=seed, scale=scale)

    nodes_data = [
        {
            "id": node,
            "label": str(node),
            # vis.js Y grows downward; NetworkX Y grows upward → flip
            "x": round(float(pos[node][0]), 2),
            "y": round(float(-pos[node][1]), 2),
            "fixed": {"x": True, "y": True},
            "color": {
                "background": "#4CAF50" if node == start else "#97C2FC",
                "border":     "#1B5E20" if node == start else "#2B7CE9",
            },
            "font": {"color": "#111111", "size": 12},
            "size": 16,
        }
        for node in sorted(G.nodes())
    ]
    edges_data = [{"from": u, "to": v} for u, v in G.edges()]
    adjacency  = {str(n): sorted(G.neighbors(n)) for n in G.nodes()}

    title_html = (
        f"<h3 style='margin:0 0 6px;font-family:sans-serif;font-size:15px'>"
        f"{title}</h3>"
        if title else ""
    )

    return _render(
        "walk.html",
        title_html  = title_html,
        nodes_json  = json.dumps(nodes_data, separators=(",", ":")),
        edges_json  = json.dumps(edges_data, separators=(",", ":")),
        adj_json    = json.dumps(adjacency,  separators=(",", ":")),
        start       = start,
        n_nodes     = G.number_of_nodes(),
        height      = height,
        start_label = str(start),
    )


def save_walk_visualization(
    G: nx.Graph,
    path: str | Path,
    *,
    start: int = 0,
    layout: str = "circular",
    height: str = "560px",
    seed: int = 42,
    scale: float = 350.0,
    title: str = "",
) -> Path:
    """Write the walk visualisation HTML to *path*.

    Parameters
    ----------
    G : networkx.Graph
        Graph to visualise.
    path : str or Path
        Destination ``.html`` file.
    start, layout, height, seed, scale, title
        Forwarded verbatim to `build_walk_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_walk_visualization(
            G,
            start=start, layout=layout, height=height,
            seed=seed, scale=scale, title=title,
        ),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Cover-time simulation visualisation
# ---------------------------------------------------------------------------

def build_cover_time_visualization(
    G: nx.Graph,
    *,
    title: str = "",
) -> str:
    """Generate a self-contained HTML page for interactive cover-time simulation.

    The page embeds the graph adjacency list and runs the cover-time algorithm
    entirely in JavaScript, so no server is required.  Users can choose the
    number of simulations and view the resulting distribution as a histogram.

    Parameters
    ----------
    G : networkx.Graph
        Graph to simulate on.
    title : str, default ``""``
        Optional heading rendered above the controls.

    Returns
    -------
    str
        A complete, UTF-8 HTML document.
    """
    adjacency = {str(n): sorted(G.neighbors(n)) for n in G.nodes()}
    title_html = f"<h3>{title}</h3>" if title else ""

    return _render(
        "cover_time.html",
        title_html = title_html,
        adj_json   = json.dumps(adjacency, separators=(",", ":")),
        n_nodes    = G.number_of_nodes(),
    )


def save_cover_time_visualization(
    G: nx.Graph,
    path: str | Path,
    *,
    title: str = "",
) -> Path:
    """Write the cover-time visualisation HTML to *path*.

    Parameters
    ----------
    G : networkx.Graph
        Graph to simulate on.
    path : str or Path
        Destination ``.html`` file.
    title : str, default ``""``
        Forwarded to `build_cover_time_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_cover_time_visualization(G, title=title),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Side-by-side comparison (Ring / WS / ER)
# ---------------------------------------------------------------------------

def build_compare_times_visualization(
    *,
    N: int = 30,
    k: int = 4,
    beta: float = 0.1,
) -> str:
    """Generate the interactive comparison page (Ring / WS / ER).

    The page builds all three graphs entirely in JavaScript and lets the user
    run animated cover-time walks and mixing-time simulations side by side.
    No server or NetworkX graph is required — everything is self-contained.

    Parameters
    ----------
    N : int, default 30
        Initial number of nodes shown in the UI slider.
    k : int, default 4
        Initial mean degree shown in the UI slider.
    beta : float, default 0.1
        Initial Watts–Strogatz rewiring probability (must be in ``(0, 1]``).

    Returns
    -------
    str
        A complete, UTF-8 HTML document ready to be saved or embedded.
    """
    beta = max(1e-4, min(1.0, beta))
    return _render(
        "compare_times.html",
        N          = N,
        k          = k,
        beta_log10 = f"{math.log10(beta):.4f}",
        beta_str   = f"{beta:.3f}",
    )


def save_compare_times_visualization(
    path: str | Path,
    *,
    N: int = 30,
    k: int = 4,
    beta: float = 0.1,
) -> Path:
    """Write the compare-times visualisation HTML to *path*.

    Parameters
    ----------
    path : str or Path
        Destination ``.html`` file.
    N, k, beta
        Forwarded to `build_compare_times_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_compare_times_visualization(N=N, k=k, beta=beta),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Metric-analytics visualisation (L and C across β, k slider)
# ---------------------------------------------------------------------------

def compute_metrics_data(
    *,
    N: int,
    k_values: list[int],
    betas: list[float],
    seed: int,
) -> dict:
    """Pre-compute (L, C) for ring / ER / WS across every (k, β) combination.

    Used internally by `build_metrics_analytics_visualization`.

    Both metrics are routed through the project's own hand-written
    implementations.  The average path length $L$ is computed on the
    largest connected component when the graph is disconnected (typical for
    ER at small ``k``), matching the convention of `camí_mig`.

    Parameters
    ----------
    N : int
        Number of nodes.
    k_values : list[int]
        Even average degrees to sweep over.
    betas : list[float]
        Rewiring probabilities at which to evaluate Watts–Strogatz.
    seed : int
        Seed shared by all builders for reproducibility.

    Returns
    -------
    dict
        Nested mapping keyed first by ``str(k)`` (JSON-friendly), then by
        network name (``"ring"``, ``"er"``, ``"ws"``).  For ``"ws"`` the
        inner level is keyed by ``str(beta)`` and holds ``{"L": …, "C": …}``.
    """
    from src.smallworld.calculate_metrics import camí_mig, coef_clusterització
    from src.smallworld.networks import build_er, build_ring, build_ws

    def safe_apl(G: nx.Graph) -> float:
        return float(camí_mig(G))

    def safe_C(G: nx.Graph) -> float:
        return float(coef_clusterització(G))

    out: dict = {}
    for k in k_values:
        print(f"  · k = {k:3d} ... ", end="", flush=True)
        Gr = build_ring(N, k, seed=seed)
        Ge = build_er(N, k, seed=seed)
        entry = {
            "ring": {"L": safe_apl(Gr), "C": safe_C(Gr)},
            "er":   {"L": safe_apl(Ge), "C": safe_C(Ge)},
            "ws":   {},
        }
        for beta in betas:
            Gw = build_ws(N, k, beta, seed=seed)
            # `:g` matches JS's Number.toString format (no trailing ".0"),
            # so the lookup in the embedded JS works for every β.
            entry["ws"][f"{beta:g}"] = {"L": safe_apl(Gw), "C": safe_C(Gw)}
        out[str(k)] = entry
        print("done")
    return out


def build_metrics_analytics_visualization(
    *,
    N: int = 1000,
    k_values: list[int] | None = None,
    betas: list[float] | None = None,
    k_default: int = 10,
    seed: int = 42,
) -> str:
    """Generate the self-contained HTML page for the *Metric analytics* section.

    Pre-computes $L(\beta)$ and $C(\beta)$ for the three
    reference networks across the requested ``(k, β)`` grid and embeds the
    table as JSON inside the page.  The browser does no metric computation,
    so the slider stays interactive even at ``N = 1000``.

    Parameters
    ----------
    N : int, default 1000
        Number of nodes used for every realisation. Displayed prominently
        in the page header so readers know the regime.
    k_values : list[int], optional
        Average degrees to sweep over. Must all be even (so that the ring
        and WS builders accept them). Defaults to ``[10, 20, …, 100]``.
    betas : list[float], optional
        Rewiring probabilities to evaluate WS at, spaced one decade apart
        so they are equidistant on the log-β axis.
        Defaults to ``[0.0001, 0.001, 0.01, 0.1, 1]``.
    k_default : int, default 10
        Slider position the page opens on. Must appear in ``k_values``.
    seed : int, default 42
        Shared random seed for every builder, so the page is reproducible.

    Returns
    -------
    str
        A complete, UTF-8 HTML document ready to be saved or embedded.
    """
    if k_values is None:
        k_values = list(range(10, 101, 10))
    if betas is None:
        betas = [0.0001, 0.001, 0.01, 0.1, 1.0]

    print(f"Building metric-analytics data  (N={N}) ...")
    data = compute_metrics_data(
        N=N, k_values=k_values, betas=betas, seed=seed,
    )

    betas_pretty = ",  ".join(
        f"{b:g}" for b in betas
    )

    return _render(
        "metrics_analytics.html",
        N             = N,
        k_max_idx     = len(k_values) - 1,
        k_default     = k_default,
        k_values_json = json.dumps(k_values),
        betas_json    = json.dumps(betas),
        betas_pretty  = betas_pretty,
        data_json     = json.dumps(data),
    )


def save_metrics_analytics_visualization(
    path: str | Path,
    *,
    N: int = 1000,
    k_values: list[int] | None = None,
    betas: list[float] | None = None,
    k_default: int = 10,
    seed: int = 42,
) -> Path:
    """Write the metric-analytics visualisation HTML to *path*.

    Parameters
    ----------
    path : str or Path
        Destination ``.html`` file.
    N, k_values, betas, k_default, seed
        Forwarded to `build_metrics_analytics_visualization`.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_metrics_analytics_visualization(
            N=N,
            k_values=k_values,
            betas=betas,
            k_default=k_default,
            seed=seed,
        ),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Metrics-analytics render from cached data
# ---------------------------------------------------------------------------

def build_metrics_analytics_from_data(
    data: dict,
    *,
    N: int = 1000,
    k_values: list[int] | None = None,
    betas: list[float] | None = None,
    k_default: int = 10,
) -> str:
    """Render the metrics-analytics HTML from a precomputed data dict.

    Separates the slow computation (`compute_metrics_data`) from the
    fast template render so cached data can be reused when only the template
    changes.  The template is always re-read from disk on each call.

    Parameters
    ----------
    data : dict
        Output of `compute_metrics_data`.
    N, k_values, betas, k_default
        Same meaning as in `build_metrics_analytics_visualization`.

    Returns
    -------
    str
        A complete, UTF-8 HTML document.
    """
    if k_values is None:
        k_values = list(range(10, 101, 10))
    if betas is None:
        betas = [0.0001, 0.001, 0.01, 0.1, 1.0]

    betas_pretty = ",  ".join(f"{b:g}" for b in betas)
    return _render(
        "metrics_analytics.html",
        N             = N,
        k_max_idx     = len(k_values) - 1,
        k_default     = k_default,
        k_values_json = json.dumps(k_values),
        betas_json    = json.dumps(betas),
        betas_pretty  = betas_pretty,
        data_json     = json.dumps(data),
    )


# ---------------------------------------------------------------------------
# Facebook real-network analysis visualisation
# ---------------------------------------------------------------------------

def build_facebook_visualization(
    fit_result: dict,
    sigma_result: dict,
) -> str:
    """Generate a self-contained HTML page for the Facebook β-fitting analysis.

    Embeds all precomputed data as JSON and renders two Chart.js charts:

    1. **Normalised (L, C) space** — the WS β-curve from ring to random,
       the real Facebook network point, and the best-fit β* marker.
    2. **σ breakdown** — bar chart of C_real/C_rand and L_real/L_rand
       with the σ value in the title.

    Parameters
    ----------
    fit_result : dict
        Output of `fit_ws`.
    sigma_result : dict
        Output of `smallworldness_sigma`.

    Returns
    -------
    str
        A complete, UTF-8 HTML document ready to be saved or embedded.
    """
    best_idx = next(
        i for i, t in enumerate(fit_result["beta_curve"])
        if t[0] == fit_result["beta_optimal"]
    )
    return _render(
        "facebook_analysis.html",
        beta_curve_json = json.dumps(fit_result["beta_curve"]),
        L_real_norm     = round(fit_result["L_real_norm"], 6),
        C_real_norm     = round(fit_result["C_real_norm"], 6),
        best_idx        = best_idx,
        beta_optimal    = f"{fit_result['beta_optimal']:.4f}",
        C_ratio         = round(sigma_result["C_real"] / sigma_result["C_rand"], 4),
        L_ratio         = round(sigma_result["L_real"] / sigma_result["L_rand"], 4),
        sigma           = f"{sigma_result['sigma']:.2f}",
        N               = fit_result["N"],
        k               = fit_result["k"],
        C_real          = f"{sigma_result['C_real']:.4f}",
        L_real          = f"{sigma_result['L_real']:.4f}",
    )


def save_facebook_visualization(
    fit_result: dict,
    sigma_result: dict,
    path: str | Path,
) -> Path:
    """Write the Facebook analysis visualisation HTML to *path*.

    Parameters
    ----------
    fit_result : dict
        Output of `fit_ws`.
    sigma_result : dict
        Output of `smallworldness_sigma`.
    path : str or Path
        Destination ``.html`` file.

    Returns
    -------
    Path
        The path the file was written to.
    """
    path = Path(path)
    path.write_text(
        build_facebook_visualization(fit_result, sigma_result),
        encoding="utf-8",
    )
    return path
