"""Generate all HTML example files for the MkDocs documentation.

Run from the project root::

    python scripts/build_examples.py

Or via the Makefile targets ``make docs`` / ``make docs-serve``, which
call this script automatically before serving/building.

Outputs
-------
``docs/examples/ring.html``
    Regular ring lattice - static pyvis view.
``docs/examples/er.html``
    Erdos-Renyi graph - static pyvis view.
``docs/examples/ws.html``
    Watts-Strogatz graph - static pyvis view.
``docs/examples/walk_ring.html``
    Ring lattice with interactive random-walk controls.
``docs/examples/walk_er.html``
    Erdos-Renyi graph with interactive random-walk controls.
``docs/examples/walk_ws.html``
    Watts-Strogatz graph with interactive random-walk controls.
``docs/examples/cover_ring.html``
    Ring lattice - interactive cover-time histogram.
``docs/examples/cover_er.html``
    Erdos-Renyi - interactive cover-time histogram.
``docs/examples/cover_ws.html``
    Watts-Strogatz - interactive cover-time histogram.
``docs/examples/compare_times.html``
    Side-by-side cover-time and mixing-time comparison (Ring / WS / ER).
``docs/examples/metrics_analytics.html``
    Interactive L(β) and C(β) panels at N = 1000, with a slider for the
    average degree k (10, 20, …, 100).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure the project root is on sys.path so ``src`` imports work.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.smallworld.networks import build_all
from src.smallworld.plotting import to_pyvis, save_pyvis
from src.smallworld.visualization import (
    save_walk_visualization,
    save_cover_time_visualization,
    save_compare_times_visualization,
    save_metrics_analytics_visualization,
)

# ── parameters ────────────────────────────────────────────────────────────────
N    = 30
K    = 4
BETA = 0.1
SEED = 42

OUT_DIR = ROOT / "docs" / "examples"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── build networks ────────────────────────────────────────────────────────────
print(f"Building networks  (N={N}, k={K}, beta={BETA}) ...")
graphs = build_all(N, K, beta=BETA, seed=SEED)

# ── static pyvis views ────────────────────────────────────────────────────────
STATIC_LAYOUTS = {"ring": "circular", "er": "spring", "ws": "circular"}

for name, G in graphs.items():
    layout = STATIC_LAYOUTS[name]
    net    = to_pyvis(G, layout=layout, seed=SEED, physics=True)
    dest   = save_pyvis(net, OUT_DIR / f"{name}.html")
    print(f"  [ok] {dest.relative_to(ROOT)}")

# ── interactive walk views ────────────────────────────────────────────────────
WALK_CFG = {
    "ring": {"layout": "circular", "title": "Ring lattice - random walk"},
    "er":   {"layout": "spring",   "title": "Erdos-Renyi - random walk"},
    "ws":   {"layout": "circular", "title": "Watts-Strogatz - random walk"},
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
    print(f"  [ok] {dest.relative_to(ROOT)}")

# ── cover-time simulation views ───────────────────────────────────────────────
COVER_CFG = {
    "ring": {"title": "Ring lattice - cover time"},
    "er":   {"title": "Erdos-Renyi - cover time"},
    "ws":   {"title": "Watts-Strogatz (beta=0.1) - cover time"},
}

for name, G in graphs.items():
    cfg  = COVER_CFG[name]
    dest = save_cover_time_visualization(
        G,
        OUT_DIR / f"cover_{name}.html",
        title=cfg["title"],
    )
    print(f"  [ok] {dest.relative_to(ROOT)}")

# ── compare-times page (Ring / WS / ER side-by-side) ────────────────────────
dest = save_compare_times_visualization(
    OUT_DIR / "compare_times.html",
    N=N, k=K, beta=BETA,
)
print(f"  [ok] {dest.relative_to(ROOT)}")

# ── metric-analytics page (L(β) and C(β) sweeps, fixed N = 1000) ────────────
# This pre-computes 10 k × 7 β = 70 Watts–Strogatz realisations plus the
# ring and ER baselines, so it takes ~1-3 minutes the first time you run it.
dest = save_metrics_analytics_visualization(
    OUT_DIR / "metrics_analytics.html",
    N=1000,
    k_values=list(range(10, 101, 10)),
    betas=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
    k_default=10,
    seed=SEED,
)
print(f"  [ok] {dest.relative_to(ROOT)}")

print(f"Done.  All HTML files written to {OUT_DIR.relative_to(ROOT)}")
