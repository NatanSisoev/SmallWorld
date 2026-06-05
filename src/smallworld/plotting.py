"""Plotting helpers for the small-world study.

Static and interactive visualisation:

* `draw_networks_grid` — side-by-side matplotlib figure, one subplot
  per network.  Used for report figures.
* `to_pyvis` / `save_pyvis` — interactive HTML rendering via `pyvis`.
* `plot_cover_time` — histogram of Monte-Carlo cover-time results.
* `plot_mixing_time_distribution` — bar chart of the stationary
  distribution estimated by `mixing_time`.

All grid/pyvis helpers accept the ``{"ring", "er", "ws"}`` naming convention
used by `build_all`, but work with any string keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import numpy.typing as npt
from matplotlib.figure import Figure

__all__ = [
    "draw_networks_grid",
    "to_pyvis",
    "save_pyvis",
    "plot_cover_time",
    "plot_mixing_time_distribution",
]


_DEFAULT_LAYOUTS: dict[str, str] = {
    "ring": "circular",
    "er": "spring",
    "ws": "circular",
}

_DEFAULT_TITLES: dict[str, str] = {
    "ring": "Regular ring lattice",
    "er": "Erdős-Rényi",
    "ws": "Watts-Strogatz",
}


def draw_networks_grid(
    graphs: Mapping[str, nx.Graph],
    *,
    layouts: Mapping[str, str] | None = None,
    titles: Mapping[str, str] | None = None,
    node_size: int = 80,
    figsize: tuple[float, float] = (15, 5),
    seed: int = 42,
    save: str | Path | None = None,
) -> Figure:
    """Draw several networks side-by-side with matplotlib.

    Parameters
    ----------
    graphs : Mapping[str, networkx.Graph]
        Networks to render, typically the output of `build_all`.
    layouts : Mapping[str, str], optional
        Per-network layout, either ``"circular"`` or ``"spring"``.
        Defaults to circular for ``ring``/``ws`` and spring for ``er``.
    titles : Mapping[str, str], optional
        Per-network subplot title. Defaults to human-readable names.
    node_size : int, default 80
        Marker size passed to `networkx.draw_networkx_nodes`.
    figsize : tuple, default ``(15, 5)``
        Matplotlib figure size.
    seed : int, default 42
        Seed for the spring layout (kept for reproducibility).
    save : str or Path, optional
        If given, the figure is saved to this path at 150 dpi.

    Returns
    -------
    matplotlib.figure.Figure
        The figure object, so the caller can further customise or save.

    Raises
    ------
    ValueError
        If an unknown layout name is passed for any network.
    """
    layouts = dict(_DEFAULT_LAYOUTS, **(layouts or {}))
    titles = dict(_DEFAULT_TITLES, **(titles or {}))

    fig, axes = plt.subplots(1, len(graphs), figsize=figsize)
    if len(graphs) == 1:
        axes = [axes]

    for ax, (name, G) in zip(axes, graphs.items()):
        pos = _layout(G, layouts.get(name, "spring"), seed=seed)
        nx.draw_networkx_nodes(
            G, pos, ax=ax, node_size=node_size, node_color="#1f77b4"
        )
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.4, width=1)
        ax.set_title(titles.get(name, name))
        ax.set_axis_off()

    fig.tight_layout()
    if save is not None:
        fig.savefig(Path(save), dpi=150, bbox_inches="tight")
    return fig


def to_pyvis(
    G: nx.Graph,
    *,
    layout: str = "spring",
    height: str = "600px",
    width: str = "100%",
    physics: bool = False,
    seed: int = 42,
):
    """Build a `pyvis.network.Network` from a NetworkX graph.

    Node positions are pre-computed with a NetworkX layout so the
    rendering is reproducible. Physics simulation is off by default so
    the graph keeps the initial shape; set ``physics=True`` to let pyvis
    relax the layout on load.

    Parameters
    ----------
    G : networkx.Graph
        Graph to render.
    layout : {"circular", "spring"}, default ``"spring"``
        Layout used to position nodes.
    height : str, default ``"600px"``
        CSS height of the iframe.
    width : str, default ``"100%"``
        CSS width of the iframe.
    physics : bool, default False
        Whether pyvis should run its force simulation.
    seed : int, default 42
        Seed for the spring layout.

    Returns
    -------
    pyvis.network.Network
        The configured network object. Use `save_pyvis` to write it to
        disk (UTF-8 safe), or `.show(path)` to display it inside a
        Jupyter notebook.

    Raises
    ------
    ValueError
        If an unknown layout name is passed.
    """
    from pyvis.network import Network

    pos = _layout(G, layout, seed=seed, scale=400.0)

    H = G.copy()
    for node, (x, y) in pos.items():
        H.nodes[node]["x"] = float(x)
        H.nodes[node]["y"] = float(y)
        H.nodes[node]["physics"] = physics
        H.nodes[node]["label"] = str(node)

    net = Network(
        height=height,
        width=width,
        bgcolor="#ffffff",
        cdn_resources="in_line",
    )
    net.from_nx(H)
    if not physics:
        net.toggle_physics(False)
    return net


def save_pyvis(net, path: str | Path) -> Path:
    """Write a pyvis network to disk as UTF-8 HTML.

    Applies two fixes on top of the raw pyvis output:

    1. **Encoding** — pyvis's `Network.save_graph` opens the file
       with the system encoding (``cp1252`` on Windows) and crashes on
       non-Latin-1 characters in the bundled JavaScript.  We call
       `Network.generate_html` and write with explicit UTF-8.
    2. **Iframe compatibility** — injects a minimal CSS reset so the
       graph fills its ``<iframe>`` container without scrollbars, rather
       than overflowing at the hardcoded ``height: 600px`` default.

    Parameters
    ----------
    net : pyvis.network.Network
        The network to serialise.
    path : str or Path
        Destination ``.html`` path.

    Returns
    -------
    Path
        The path the file was written to.
    """
    # CSS injected just before </head> so it overrides pyvis's own rules.
    _IFRAME_CSS = (
        "<style>"
        "html,body{margin:0;padding:0;height:100%;overflow:hidden;}"
        "div.card{height:100%;margin:0;border:0;padding:0;}"
        "#mynetwork{height:100%!important;border:0!important;}"
        "</style>"
    )
    html = net.generate_html()
    html = html.replace("</head>", _IFRAME_CSS + "\n</head>", 1)
    path = Path(path)
    path.write_text(html, encoding="utf-8")
    return path


def _layout(
    G: nx.Graph, kind: str, *, seed: int = 42, scale: float = 1.0
) -> dict:
    """Compute a node-position dictionary for the requested layout."""
    if kind == "circular":
        return nx.circular_layout(G, scale=scale)
    if kind == "spring":
        return nx.spring_layout(G, seed=seed, scale=scale)
    raise ValueError(f"Unknown layout {kind!r}; use 'circular' or 'spring'.")


# ---------------------------------------------------------------------------
# Simulation result plots
# ---------------------------------------------------------------------------

def plot_cover_time(
    steps_by_sim: list[int],
    name_graph: str | None = None,
    *,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot a histogram of cover-time simulation results.

    Parameters
    ----------
    steps_by_sim : list[int]
        Raw output from `cover_time` — number of steps for each simulation run.
    name_graph : str, optional
        Graph name used in the plot title.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on.  A new figure is created when ``None``.

    Returns
    -------
    matplotlib.figure.Figure
        The figure object.
    """
    steps_arr = np.asarray(steps_by_sim)
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    else:
        fig = ax.get_figure()

    n_bins = max(1, len(np.unique(steps_arr)))
    ax.hist(steps_arr, bins=n_bins, color="skyblue", edgecolor="black")
    ax.set_xlabel("Number of steps")
    ax.set_ylabel("Frequency")
    title = f"Cover Time — {name_graph}" if name_graph else "Cover Time"
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    return fig


def plot_mixing_time_distribution(
    prob_distribution: npt.ArrayLike,
    name_graph: str | None = None,
    *,
    ax: plt.Axes | None = None,
) -> plt.Figure:
    """Plot the stationary-distribution estimate from a mixing-time run.

    Parameters
    ----------
    prob_distribution : array-like
        Either a 1-D array of length *N* (single distribution) or a 2-D
        array of shape ``(n_simulations, N)`` — distributions are averaged
        before plotting in the latter case.
    name_graph : str, optional
        Graph name used in the plot title.
    ax : matplotlib.axes.Axes, optional
        Axes to draw on.  A new figure is created when ``None``.

    Returns
    -------
    matplotlib.figure.Figure
        The figure object.
    """
    dist = np.asarray(prob_distribution, dtype=float)
    if dist.ndim == 2:
        dist = dist.mean(axis=0)

    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4.5))
    else:
        fig = ax.get_figure()

    x = np.arange(len(dist))
    ax.bar(x, dist, width=0.75, edgecolor="black", linewidth=0.8, alpha=0.85)
    ax.set_xlabel("Node", fontsize=12)
    ax.set_ylabel(r"$P(X = i)$", fontsize=12)
    title = (
        f"Stationary Distribution — {name_graph}" if name_graph
        else "Stationary Distribution"
    )
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_ylim(0, dist.max() * 1.15)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    fig.tight_layout()
    return fig
