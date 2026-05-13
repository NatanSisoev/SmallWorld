"""Generate the interactive pyvis HTML examples embedded in the docs.

Writes one HTML file per reference network into ``docs/examples/``. The
docs page ``docs/examples.md`` references these via ``<iframe>``.

Invoked automatically by ``make docs`` and ``make docs-serve``.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.smallworld.networks import build_all
from src.smallworld.plotting import save_pyvis, to_pyvis

OUT = ROOT / "docs" / "examples"
OUT.mkdir(parents=True, exist_ok=True)

LAYOUTS = {"ring": "circular", "er": "spring", "ws": "circular"}

N, k, beta = 50, 10, 0.1
graphs = build_all(N=N, k=k, beta=beta, seed=42)

for name, G in graphs.items():
    net = to_pyvis(G, layout=LAYOUTS[name], height="500px", physics=True)
    out = save_pyvis(net, OUT / f"{name}.html")
    print(f"wrote {out.relative_to(ROOT)}")
