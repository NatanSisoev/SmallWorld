"""Generate all HTML example files for the MkDocs documentation.

Run from the project root::

    python scripts/build_examples.py

Or via the Makefile targets ``make docs`` / ``make docs-serve``, which
call this script automatically before serving/building.

Outputs
-------
``docs/examples/ring.html``
    Regular ring lattice – static pyvis view.
``docs/examples/er.html``
    Erdős–Rényi graph – static pyvis view.
``docs/examples/ws.html``
    Watts–Strogatz graph – static pyvis view.
``docs/examples/walk_ring.html``
    Ring lattice with interactive random-walk controls.
``docs/examples/walk_er.html``
    Erdős–Rényi graph with interactive random-walk controls.
``docs/examples/walk_ws.html``
    Watts–Strogatz graph with interactive random-walk controls.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure the project root is on sys.path so ``src`` imports work.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.smallworld.networks import build_all
from src.smallworld.plotting import to_pyvis, save_pyvis
from src.smallworld.visualization import save_walk_visualization

# ── parameters ────────────────────────────────────────────────────────────────
N    = 30
K    = 4
BETA = 0.1
SEED = 42

OUT_DIR = ROOT / "docs" / "examples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── build networks ────────────────────────────────────────────────────────────
print("Building networks  (N={}, k={}, β={})…".format(N, K, BETA))
graphs = build_all(N, K, beta=BETA, seed=SEED)

# ── static pyvis views ────────────────────────────────────────────────────────
STATIC_LAYOUTS = {"ring": "circular", "er": "spring", "ws": "circular"}

for name, G in graphs.items():
    layout = STATIC_LAYOUTS[name]
    net    = to_pyvis(G, layout=layout, seed=SEED, physics=True)
    dest   = save_pyvis(net, OUT_DIR / f"{name}.html")
    print(f"  ✓ {dest.relative_to(ROOT)}")

# ── interactive walk views ────────────────────────────────────────────────────
WALK_CFG = {
    "ring": {"layout": "circular", "title": "Ring lattice – random walk"},
    "er":   {"layout": "spring",   "title": "Erdős–Rényi – random walk"},
    "ws":   {"layout": "circular", "title": "Watts–Strogatz – random walk"},
}

for name, G in graphs.items():
    cfg  = WALK_CFG[name]
    dest = save_walk_visualization(
        G,
        OUT_DIR / f"walk_{name}.html",
        start=0,
        layout=cfg["layout"],
        seed=SEED,
        title=cfg["title"],
    )
    print(f"  ✓ {dest.relative_to(ROOT)}")

print("Done.  All HTML files written to", OUT_DIR.relative_to(ROOT))
