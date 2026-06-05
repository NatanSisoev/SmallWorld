"""SmallWorld — course project for Modelització i Simulació (MatCAD, UAB).

Implements the Watts-Strogatz small-world network model from scratch.
`networkx.Graph` is used only as a container; every algorithmic
step (construction, metrics, random walks) is written by hand.

Submodules
----------
networks
    By-hand graph builders: ring, Erdős-Rényi, Watts-Strogatz.
networks_nx
    Reference implementation (delegates to NetworkX) kept for equivalence
    testing.
plotting
    Static matplotlib figures and interactive pyvis HTML views; also
    cover-time and mixing-time result plots.
simulation
    Random-walk primitives, stationary distribution, transition matrix,
    cover-time and mixing-time estimators.
visualization
    Self-contained HTML pages (vis.js) for interactive walk and
    cover-time / mixing-time exploration; loaded from ``templates/``.
"""

from src.smallworld.networks import build_all, build_er, build_ring, build_ws
from src.smallworld.simulation import (
    cover_time,
    mixing_time,
    random_walk,
    random_walk_step,
    stationary_distribution,
)

__all__ = [
    # network builders
    "build_all",
    "build_er",
    "build_ring",
    "build_ws",
    # simulation
    "cover_time",
    "mixing_time",
    "random_walk",
    "random_walk_step",
    "stationary_distribution",
]
