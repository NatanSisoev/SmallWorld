"""Plotting helpers for the small-world study.

Two visualisation modes are exposed:

* :func:`draw_networks_grid` — static side-by-side matplotlib figure,
  one subplot per network. Used for the report figures.
* :func:`to_pyvis` — interactive HTML rendering via :mod:`pyvis`. Useful
  for exploration: nodes are draggable and the graph can be zoomed.

Both helpers expect the ``{"ring", "er", "ws"}`` naming convention used
by :func:`src.networks.build_all`, but accept any string keys.
"""

from __future__ import annotations

from pathlib import Path
from typing import Mapping

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.figure import Figure

__all__ = ["draw_networks_grid", "to_pyvis", "save_pyvis"]


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
        Networks to render, typically the output of
        :func:`src.networks.build_all`.
    layouts : Mapping[str, str], optional
        Per-network layout, either ``"circular"`` or ``"spring"``.
        Defaults to circular for ``ring``/``ws`` and spring for ``er``.
    titles : Mapping[str, str], optional
        Per-network subplot title. Defaults to human-readable names.
    node_size : int, default 80
        Marker size passed to :func:`networkx.draw_networkx_nodes`.
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
    """Build a :class:`pyvis.network.Network` from a NetworkX graph.

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
        Call ``.save_graph(path)`` to write the HTML, or ``.show(path)``
        to display it inline inside a Jupyter notebook.
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

    Works around a Windows-specific bug where :meth:`Network.save_graph`
    opens the output file with the system encoding (``cp1252``) and
    crashes on non-Latin-1 characters embedded in the bundled JavaScript.

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
    path = Path(path)
    path.write_text(net.generate_html(), encoding="utf-8")
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
