# SmallWorld

Documentation for the **Modelització i Simulació** course project
(MatCAD, UAB, 2025–2026).

In 1967, Stanley Milgram observed that two random Americans are
connected by a chain of about **six acquaintances**. Three decades
later, Watts & Strogatz (*Nature*, 1998) showed that this is a
generic feature of networks that combine **high local clustering**
with **a few random long-range shortcuts**. This project reproduces
their analysis.

We build and study three reference networks at the same average
degree $k$:

- a regular **ring lattice** — every node connected to its
  $k/2$ nearest neighbours,
- an **Erdős–Rényi** random graph — each edge sampled independently
  with probability $p = k / (N-1)$,
- a **Watts–Strogatz** small-world graph — rewire each ring edge
  with probability $\beta$.

For each we compute the **average path length** $L$ and **clustering
coefficient** $C$, sweep $\beta \in [10^{-3}, 1]$ to locate the
small-world window, and simulate random walks to estimate **cover
time** and **mixing time**.

!!! tip "Where to start"
    - Curious about the math? → [Theory](theory.md)
    - Looking for a function? → [API Reference](api/networks.md)
    - Want to run the experiments? → see *Getting started* below.

## Code layout

```text
SmallWorld/
├── src/smallworld/               importable library
│   ├── networks.py               builders for the three networks
│   ├── plotting.py               matplotlib + pyvis helpers
│   └── ...
├── notebooks/                    experiments — run in order
│   ├── 01_visualise_networks.ipynb
│   ├── 02_basic_metrics.ipynb
│   ├── 03_small_world_window.ipynb
│   └── 04_random_walks.ipynb
├── docs/                         this documentation
└── figures/                      generated plots and pyvis HTML
```

## Getting started

```bash
make install     # install dependencies (mkdocs, networkx, pyvis, ...)
make docs-serve  # live-reloading docs at http://localhost:8000
jupyter lab      # open the notebooks
```

To build a static HTML site instead, run `make docs` — the result is
written to `site/`.

## Authors

- Lluís Gay
- Sergi Prats
- Ferran Villarta
- Natan Sisoev
