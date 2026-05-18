"""SmallWorld - library code for the small-world course project.

The construction algorithms (ring, ER, WS) are written by hand;
:class:`networkx.Graph` is used only as the underlying container so
visualisation and standard graph utilities keep working.

Submodules
----------
* :mod:`src.smallworld.networks`    - by-hand graph builders.
* :mod:`src.smallworld.networks_nx` - reference implementation using
  NetworkX's own constructors, kept for equivalence testing.
* :mod:`src.smallworld.plotting`    - visualisation helpers, both static
  (matplotlib) and interactive (pyvis).

Forthcoming: :mod:`metrics` (hand-written L and C) and :mod:`walks`
(random-walk simulation, cover time, mixing time).
"""

from src.smallworld.networks import build_all, build_er, build_ring, build_ws

__all__ = ["build_all", "build_er", "build_ring", "build_ws"]
