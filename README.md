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
├── requirements.txt
├── src/                          # reusable library code
│   ├── networks.py               # build_ring, build_er, build_ws
│   ├── metrics.py                # L, C, β-sweep
│   ├── walks.py                  # random walk, cover time, mixing time
│   └── plotting.py               # shared figure styling
├── notebooks/                    # experiments - run in order
│   ├── 01_visualise_networks.ipynb
│   ├── 02_basic_metrics.ipynb
│   ├── 03_small_world_window.ipynb
│   └── 04_random_walks.ipynb
├── figures/                      # generated plots
└── informe/                      # final report
```

## Setup

```bash
pip install -r requirements.txt
```

Then run the notebooks in `notebooks/` in numerical order.

## Authors

- Lluís Gay
- Sergi Prats
- Ferran Villarta
- Natan Sisoev
