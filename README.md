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
├── requirements.txt
├── src/smallworld/               # reusable library code
│   ├── networks.py               # build_ring, build_er, build_ws
│   ├── networks_nx.py            # NetworkX-based builders
│   ├── calculate_metrics.py      # L, C, β-sweep
│   ├── simulation.py             # random walk, cover time, mixing time
│   ├── real_network.py           # Facebook dataset analysis
│   ├── plotting.py               # shared figure styling
│   └── visualization.py          # interactive pyvis exports
├── notebooks/                    # experiments
│   ├── 01_visualise_networks.ipynb
│   └── 02_spectral_analysis.ipynb
├── scripts/
│   └── build_examples.py         # regenerates HTML examples in docs/
├── data/                         # cached computation results (JSON)
├── docs/                         # documentation source (mkdocs)
└── figures/                      # generated plots
```

## Setup

Requires **Python 3.10+**. It is recommended to work inside a virtual
environment to keep dependencies isolated:

```bash
python -m venv .venv
# Windows:   .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
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
