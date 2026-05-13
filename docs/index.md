# SmallWorld

Documentation for the **Modelització i Simulació** course project
(MatCAD, UAB, 2025–2026).

## What we study

In 1967, Stanley Milgram observed that two random Americans are
connected by a chain of about **six acquaintances**. Three decades
later, Watts & Strogatz (*Nature*, 1998) showed that this is a
generic feature of networks combining **high local clustering** with
**a few random long-range shortcuts**. We reproduce their analysis
on three reference networks.

## The three networks

All three are built on `N` nodes with average degree `k`:

| Network | Built by | Path length $L$ | Clustering $C$ |
|---|---|---|---|
| **Ring lattice** | each node connects to its `k/2` neighbours on each side of the ring | $\sim N / (2k)$ | $\approx 3/4$ |
| **Erdős–Rényi** | each edge sampled independently with $p = k / (N-1)$ | $\sim \log N / \log k$ | $\approx k / N$ |
| **Watts–Strogatz** | start from the ring, rewire each edge with probability $\beta$ | small for $\beta \gtrsim 10^{-2}$ | high for $\beta \lesssim 10^{-1}$ |

The Watts–Strogatz model interpolates between the two extremes. The
**small-world window** — where $L$ has already collapsed to random-graph
length but $C$ is still close to the lattice value — lies around
$\beta \in [10^{-2}, 10^{-1}]$.

## The two metrics

**Average path length**
$$L = \frac{1}{N(N-1)} \sum_{i \neq j} d(i, j)$$
where $d(i, j)$ is the shortest-path distance.

**Clustering coefficient** (global / transitivity definition)
$$C = \frac{3 \cdot \#\text{triangles}}{\#\text{paths of length } 2}$$
*i.e.* the fraction of length-2 paths that close into a triangle.

## Random walks

The simple random walk on $G$ is a Markov chain with transition
matrix $P_{ij} = 1 / d_i$ when $(i, j) \in E$. On a connected
non-bipartite graph the unique stationary distribution is
$$\pi_i = \frac{d_i}{2m},$$
which reduces to the uniform distribution when every node has the
same degree (ring lattice and Watts–Strogatz, in expectation).

We estimate two characteristic times by simulation:

* **Cover time** — expected number of steps until every node has been
  visited at least once.
* **Mixing time** — time for the walker's distribution to converge
  (in total variation) to $\pi$.

The small-world network has both times **dramatically shorter** than
the regular ring: a few shortcuts are enough to make diffusion fast.

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
├── docs/
│   ├── index.md                  ← you are here
│   └── api/                      pdoc-generated, build with `make docs`
├── figures/                      generated plots and pyvis HTML
└── informe/                      written report
```

The API reference (built by `make docs`) lives at
[`api/index.html`](api/index.html) and is auto-generated from the
docstrings in `src/smallworld/`.

## Getting started

```bash
make install     # install Python dependencies
make docs        # build the API documentation
jupyter lab      # open the notebooks
```

See the project [README](../README.md) for the team split and the
overall report structure.

## Authors

* Lluís Gay
* Sergi Prats
* Ferran Villarta
* Natan Sisoev
