"""Interactive random-walk visualisation via vis.js.

Generates self-contained HTML pages that embed a vis.js graph together
with a walk-control panel.  The pages are designed to be served as
``<iframe>`` embeds inside the MkDocs documentation site.

HTML templates live in ``src/smallworld/templates/`` and use ``@@key@@``
placeholders.  Python fills them with :func:`_render`.

The main entry points are:

* :func:`build_walk_visualization`         — HTML for one interactive walk.
* :func:`save_walk_visualization`          — write it to disk.
* :func:`build_cover_time_visualization`   — HTML for cover-time histogram.
* :func:`save_cover_time_visualization`    — write it to disk.
* :func:`build_compare_times_visualization`— HTML for side-by-side comparison.
* :func:`save_compare_times_visualization` — write it to disk.

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
        :func:`save_walk_visualization` or embed it in an ``<iframe>``.
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
        Forwarded verbatim to :func:`build_walk_visualization`.

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
        Forwarded to :func:`build_cover_time_visualization`.

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
        Forwarded to :func:`build_compare_times_visualization`.

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
