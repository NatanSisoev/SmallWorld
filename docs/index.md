# SmallWorld

Documentation for the **Modelització i Simulació** course project
(MatCAD, UAB, 2025–2026).

---

In 1967, Stanley Milgram observed that two random Americans are
connected by a chain of about **six acquaintances**. Three decades
later, Watts & Strogatz (*Nature*, 1998) showed that this emerges
naturally in networks that combine **high local clustering** with
**a few random long-range shortcuts** — the *small-world regime*.

This project reproduces their analysis. We build three reference
networks at the same $N$ and average degree $k$, measure how path
length $L$ and clustering $C$ evolve as the rewiring probability
$\beta$ increases, simulate random walks to estimate **cover time**
and **mixing time**, and validate the model against a real social
network.

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle } **Theory**

    ---

    Network models, $L$ and $C$ metrics, the small-world window,
    the $\sigma$ coefficient, random walks, and mixing time.

    [:octicons-arrow-right-24: Read Theory](theory.md)

-   :material-chart-line:{ .lg .middle } **Explore**

    ---

    Interactive demos: drag the networks, sweep $\beta$, watch a
    random walker, run cover-time simulations.

    [:octicons-arrow-right-24: Start Exploring](explore/networks.md)

-   :material-earth:{ .lg .middle } **Case Study**

    ---

    Is Facebook truly small-world? $\sigma \approx 39$. The best-fit
    Watts–Strogatz model has $\beta \approx 0.05$.

    [:octicons-arrow-right-24: View Case Study](real_network.md)

-   :material-code-tags:{ .lg .middle } **API Reference**

    ---

    Full docstrings for every function in `src/smallworld/`.

    [:octicons-arrow-right-24: Browse API](api/networks.md)

</div>

## Project layout

```text
src/smallworld/
├── networks.py           ring, Erdős–Rényi, Watts–Strogatz builders
├── calculate_metrics.py  average path length L and clustering coefficient C
├── simulation.py         random walk, cover time, mixing time
├── real_network.py       σ coefficient, β-fitting, Facebook analysis
├── plotting.py           matplotlib + pyvis helpers
├── visualization.py      interactive HTML pages (embedded in Explore)
└── networks_nx.py        NetworkX reference oracle for validation
```

```text
notebooks/
├── 01_visualise_networks.ipynb   build and render the three networks
├── 02_small_world_window.ipynb   β sweep — L and C vs β
├── 03_random_walks.ipynb         cover time and mixing time
└── 04_real_network.ipynb         Facebook case study
```

## Getting started

```bash
make install     # install dependencies
make docs-serve  # live-reloading docs at http://localhost:8000
jupyter lab      # open the notebooks
```

Without `make`:

```bash
pip install -r requirements.txt
python -m mkdocs serve
```

## Authors

Lluís Gay · Sergi Prats · Ferran Villarta · Natan Sisoev
