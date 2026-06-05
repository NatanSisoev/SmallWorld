# SmallWorld

Watts–Strogatz small-world model — course project for **Modelització i Simulació** (MatCAD, UAB, 2025–2026).

[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue?logo=github)](https://natansisoev.github.io/SmallWorld/)

**Authors:** [Lluís Gay](https://github.com/lluisgay2004) · [Sergi Prats](https://github.com/prats-codes) · [Ferran Villarta](https://github.com/Ferran-Villarta) · [Natan Sisoev](https://github.com/natansisoev)

---

## What this is

We study the Watts–Strogatz model: starting from a regular ring lattice, rewiring each edge with probability $\beta$ produces a *small-world* network — one that is simultaneously highly clustered (like the ring) and has short paths (like a random graph). This is the mechanism behind Milgram's "six degrees of separation".

The project builds three reference networks at the same $N$ and average degree $k$, computes **average path length** $L$ and **clustering coefficient** $C$ across a $\beta$ sweep, simulates random walks to estimate **cover time** and **mixing time**, and validates the model against a real social network (Facebook, 4 039 nodes, $\sigma \approx 39$).

## Documentation

The best way to navigate the project is the documentation website:

**https://natansisoev.github.io/SmallWorld/**

It includes:
- **Theory** — mathematical background (network models, metrics, random walks, mixing time)
- **Explore** — interactive demos (drag networks, sweep $\beta$, watch a random walker)
- **Case Study** — Facebook network analysis
- **API Reference** — docstrings for every function

To build and serve the docs locally:

```bash
make install      # install all dependencies
make docs-serve   # live-reloading site at http://localhost:8000
```

## Quick start

Python 3.10+ required.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

Open the notebooks in order:

```bash
jupyter lab
```

| Notebook | Content |
|---|---|
| `01_visualise_networks.ipynb` | Build and render the three networks |
| `02_small_world_window.ipynb` | $\beta$ sweep — $L$ and $C$ vs $\beta$ |
| `03_random_walks.ipynb` | Cover time and mixing time |
| `04_real_network.ipynb` | Facebook case study |

## Repository structure

```text
SmallWorld/
├── src/smallworld/
│   ├── networks.py           ring, Erdős–Rényi, Watts–Strogatz builders
│   ├── calculate_metrics.py  average path length L and clustering coefficient C
│   ├── simulation.py         random walk, cover time, mixing time
│   ├── real_network.py       σ coefficient, β-fitting, Facebook analysis
│   ├── plotting.py           matplotlib + pyvis helpers
│   ├── visualization.py      interactive HTML pages
│   └── networks_nx.py        NetworkX reference oracle for validation
├── notebooks/                experiments — run in order
├── docs/                     documentation source (MkDocs + Material)
├── scripts/
│   └── build_examples.py     generates interactive HTML for the docs
├── tests/
│   ├── test_unit_calculate_metrics.py
│   └── test_unit_simulation.py
├── data/                     cached computation results
├── mkdocs.yml
├── Makefile
└── requirements.txt
```

## Tests

```bash
pytest
```

The project rule is that the mathematical core (graph construction, metrics, random walks) must be written by hand — no NetworkX helpers. The test suite verifies two things:

**Correctness against analytic ground truth** — e.g. `average_path_length(K5) == 1.0`, `clustering_coefficient(K5) == 1.0`, `average_path_length(C6) == 1.8` (computable by hand from the cycle geometry).

**Equivalence with NetworkX** — the hand-written implementations are compared against NetworkX's reference implementations on the same graphs:
- `average_path_length` vs `nx.average_shortest_path_length` (ring graphs, N = 10, 20, 50)
- `clustering_coefficient` vs `nx.transitivity` (ring, ER, and WS graphs)

If the equivalence tests pass, the manual BFS and triangle-counting code is provably correct.

## License

This project is for academic use (MatCAD, UAB).
