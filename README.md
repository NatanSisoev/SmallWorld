# SmallWorld

Course project for **Modelització i Simulació** (MatCAD, UAB, 2025–2026).

We study the **Watts–Strogatz small-world model**: build three networks
(regular ring lattice, Erdős–Rényi random graph, Watts–Strogatz),
compare their average path length $L$ and clustering coefficient $C$,
sweep the rewiring probability $\beta$ to locate the small-world window,
and simulate random walks to estimate cover time and mixing time.

## Tools

Networks are built and analysed with [NetworkX](https://networkx.org/),
and visualised interactively with [pyvis](https://pyvis.readthedocs.io/)
(HTML/JavaScript output, lets you zoom and drag nodes around).

## Structure

```
SmallWorld/
├── README.md
├── LICENSE
├── Makefile                          # install / docs / test shortcuts
├── requirements.txt
├── pytest.ini
├── mkdocs.yml                        # documentation site config
├── src/smallworld/                   # reusable library code
│   ├── networks.py                   # build_ring, build_er, build_ws (hand-built)
│   ├── networks_nx.py                # NetworkX reference builders (for equivalence tests)
│   ├── calculate_metrics.py          # camí_mig (L), coef_clusterització (C)
│   ├── simulation.py                 # random walk, stationary dist., cover & mixing time
│   ├── plotting.py                   # static + pyvis figures
│   ├── visualization.py              # interactive HTML visualisations
│   ├── real_network.py               # Facebook network: σ small-worldness, WS fitting
│   └── templates/                    # HTML templates for the interactive pages
├── notebooks/                        # experiments - run in order
│   ├── 01_visualise_networks.ipynb   # build & draw the three networks + walks
│   ├── 02_small_world_window.ipynb   # L and C vs β and k: the small-world window
│   └── 03_spectral_analysis.ipynb    # spectral gap / mixing analysis
├── scripts/
│   └── build_examples.py             # generate the documentation's interactive HTML examples
├── tests/                            # unit tests (pytest)
│   ├── test_unit_calculate_metrics.py
│   └── test_unit_simulation.py
├── data/                             # cached computation results
│   ├── metrics_analytics_data.json
│   └── facebook_cache.json
├── docs/                             # MkDocs documentation site
│   ├── index.md, theory.md, real_network.md, explore.md
│   ├── api/                          # API reference pages
│   └── examples/                     # generated interactive HTML
└── figures/                          # generated plots
```

## Setup

Create a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate     # on Windows
source .venv/bin/activate  # on macOS/Linux
```

Then install and serve:

```bash
make install      # installs dependencies from requirements.txt
make docs-serve   # live-reloading docs at http://localhost:8000
```

Then open the docs in a browser, or run the notebooks in `notebooks/`
in numerical order. To build a static site for distribution, run
`make docs` — output goes to `site/`.

Without `make`, the same commands work directly: `pip install -r
requirements.txt`, `python -m mkdocs serve`.

## Authors

- Lluís Gay
- Sergi Prats
- Ferran Villarta
- Natan Sisoev
