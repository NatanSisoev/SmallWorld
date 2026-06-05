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

import json
import sys

import numpy as np
from pathlib import Path

# Force UTF-8 stdout so progress prints with β, σ, → don't crash on the
# Windows console (cp1252 by default).
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

# Make sure the project root is on sys.path so ``src`` imports work.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.smallworld.networks import build_all
from src.smallworld.plotting import to_pyvis, save_pyvis
from src.smallworld.visualization import (
    save_walk_visualization,
    save_cover_time_visualization,
    save_compare_times_visualization,
    compute_metrics_data,
    build_metrics_analytics_from_data,
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
# Slow (1-3 min first time). Data cached to data/metrics_analytics_data.json;
# HTML always regenerated from cache + template (< 1 s, picks up template edits).
K_VALUES      = list(range(10, 101, 10))
BETAS         = [0.0001, 0.001, 0.01, 0.1, 1.0]
METRICS_CACHE = ROOT / "data" / "metrics_analytics_data.json"

if METRICS_CACHE.exists():
    print("  [cache] metrics_analytics_data.json → rendering HTML ...")
    with open(METRICS_CACHE, encoding="utf-8") as fh:
        metrics_data = json.load(fh)
else:
    print("Building metric-analytics data  (N=1000) ...")
    metrics_data = compute_metrics_data(N=1000, k_values=K_VALUES, betas=BETAS, seed=SEED)
    METRICS_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_CACHE, "w", encoding="utf-8") as fh:
        json.dump(metrics_data, fh)
    print(f"  [cache → {METRICS_CACHE.relative_to(ROOT)}]")

metrics_html = build_metrics_analytics_from_data(
    metrics_data, N=1000, k_values=K_VALUES, betas=BETAS, k_default=10,
)
(OUT_DIR / "metrics_analytics.html").write_text(metrics_html, encoding="utf-8")
print(f"  [ok] {(OUT_DIR / 'metrics_analytics.html').relative_to(ROOT)}")

# ── real network analysis (Facebook Social Circles, SNAP) ────────────────────
# Slow (5-10 min first time). Cached to data/ so subsequent runs are instant.
from src.smallworld.real_network import fit_ws, load_facebook, smallworldness_sigma
from src.smallworld.visualization import save_facebook_visualization

FB_CACHE = ROOT / "data" / "facebook_cache.json"

if FB_CACHE.exists():
    print("\nLoading Facebook results from cache ...")
    with open(FB_CACHE, encoding="utf-8") as fh:
        cached = json.load(fh)
    sigma_result = cached["sigma_result"]
    fit_result   = cached["fit_result"]
    print(f"  σ = {sigma_result['sigma']:.3f}  |  β* = {fit_result['beta_optimal']:.4f}")
else:
    print("\nLoading Facebook Social Circles dataset ...")
    G_fb = load_facebook()
    print(f"  {G_fb.number_of_nodes()} nodes, {G_fb.number_of_edges()} edges")

    print("Computing smallworldness σ  (n_random=10, n_apl_samples=100) ...")
    sigma_result = smallworldness_sigma(G_fb, n_random=10, n_apl_samples=100)
    print(f"  C_real={sigma_result['C_real']:.4f}  L_real={sigma_result['L_real']:.4f}")
    print(f"  C_rand={sigma_result['C_rand']:.4f}  L_rand={sigma_result['L_rand']:.4f}")
    print(f"  σ = {sigma_result['sigma']:.3f}")

    print("Fitting WS model (15 β values, 3 reps, n_apl_samples=100) ...")
    fit_result = fit_ws(
        G_fb,
        beta_values=list(np.logspace(-3, 0, 15)),
        n_reps=3,
        n_apl_samples=100,
        verbose=True,
    )
    print(f"  β* = {fit_result['beta_optimal']:.4f}  (distance = {fit_result['distance']:.4f})")

    FB_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(FB_CACHE, "w", encoding="utf-8") as fh:
        json.dump({"sigma_result": sigma_result, "fit_result": fit_result}, fh, indent=2)
    print(f"  [cache → {FB_CACHE.relative_to(ROOT)}]")

dest = save_facebook_visualization(fit_result, sigma_result, OUT_DIR / "facebook_analysis.html")
print(f"  [ok] {dest.relative_to(ROOT)}")

print(f"Done.  All HTML files written to {OUT_DIR.relative_to(ROOT)}")
