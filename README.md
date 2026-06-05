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
Numerical work uses NumPy/SciPy; plots are made with Matplotlib.

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
|   ├── 03_random_walks.ipynb         # TODO
|   └── 04_real_network.ipynb         # real network fitting check
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

Requires **Python 3.10+**. It is recommended to work inside a virtual
environment to keep dependencies isolated:

```bash
python -m venv .venv
.venv\Scripts\activate     # on Windows
source .venv/bin/activate  # on macOS/Linux
```

Then install and launch the docs:

```bash
make install      # installs dependencies from requirements.txt
make docs-serve   # live-reloading docs at http://localhost:8000
```

Without `make`, the same commands work directly: `pip install -r
requirements.txt`, then `python -m mkdocs serve`.

To run the notebooks, open them in VS Code (which has built-in Jupyter
support) or run `jupyter notebook` from the project folder after
installing Jupyter (`pip install jupyter`).

## Authors

- Lluís Gay
- Sergi Prats
- Ferran Villarta
- Natan Sisoev
