# Theory

## The three networks

All three are built on $N$ nodes with average degree $k$, which makes
the comparison fair.

| Network | Built by | Path length $L$ | Clustering $C$ |
|---|---|---|---|
| **Ring lattice** | every node connected to its $k/2$ neighbours on each side of the ring | $\sim N / (2k)$ | $\approx 3/4$ |
| **Erdős–Rényi** | each edge sampled independently with $p = k / (N-1)$ | $\sim \log N / \log k$ | $\approx k / N$ |
| **Watts–Strogatz** | start from the ring, rewire each edge with probability $\beta$ | small for $\beta \gtrsim 10^{-2}$ | high for $\beta \lesssim 10^{-1}$ |

The Watts–Strogatz model interpolates between the two extremes. The
**small-world window** — where $L$ has already collapsed to
random-graph length but $C$ is still close to the lattice value —
sits around $\beta \in [10^{-2}, 10^{-1}]$.

!!! example "Try it"
    - [Explore → Networks](explore/networks.md) — drag, zoom and hover each network
    - [API → Networks](api/networks.md) — `build_ring`, `build_er`, `build_ws`

## The two metrics

### Average path length

$$
L = \frac{1}{N(N-1)} \sum_{i \neq j} d(i, j)
$$

where $d(i, j)$ is the shortest-path distance, found by breadth-first
search.

!!! warning "Disconnected graphs"
    If $G$ is not connected, some $d(i, j) = \infty$ and $L$ is
    undefined. We work around this by restricting to the largest
    connected component when needed.

### Clustering coefficient

The fraction of length-2 paths that close into a triangle:

$$
C = \frac{3 \cdot \#\text{triangles}}{\#\text{paths of length } 2}
$$

This is the *global* (or transitivity) definition, implemented by
`clustering_coefficient` and used for the small-world window. The
*average local* version — average over nodes of
$c_i = 2 \cdot e_i / [d_i(d_i - 1)]$ where $e_i$ is the number of
edges among $i$'s neighbours — is the definition used in the original
Watts–Strogatz paper; the real-network case study adopts it (via
`nx.average_clustering`) when computing the $\sigma$ coefficient below.

!!! example "Try it"
    - [Explore → Metric analytics](explore/metrics.md) — sweep $\beta$ and track $L$ and $C$
    - [API → Metrics](api/metrics.md) — `average_path_length`, `clustering_coefficient`

## The small-world window

For $\beta \in \{10^{-3}, 5 \cdot 10^{-3}, 10^{-2}, 5 \cdot 10^{-2}, 10^{-1}, 0.5, 1\}$
compute $L(\beta)$ and $C(\beta)$, normalise by their $\beta = 0$
value, and plot both on the same log-x figure. The expected shape:

- $L(\beta)/L(0)$ drops near-vertically around $\beta \sim 10^{-2}$.
- $C(\beta)/C(0)$ stays near 1 until $\beta \sim 10^{-1}$, then drops.

The gap between the two curves *is* the small-world regime. A single
shortcut shortens many pairwise distances at once but destroys only a
few triangles locally — that's why the two collapse on different
scales.

!!! example "Try it"
    - [Explore → Metric analytics](explore/metrics.md) — $L$ and $C$ vs $\beta$ sweep
    - [Explore → Side-by-side: effect of β](explore/cover_time.md#side-by-side-effect-of-beta) — compare all three networks in real time

## Quantifying small-worldness: the $\sigma$ coefficient

Identifying the small-world window visually is intuitive, but comparing
different real-world networks requires a single scalar. Humphries & Gurney
(2008) propose the **smallworldness coefficient**:

$$
\sigma = \frac{C / C_{\text{rand}}}{L / L_{\text{rand}}}
$$

where $C_{\text{rand}}$ and $L_{\text{rand}}$ are the clustering coefficient
and average path length of an Erdős–Rényi graph with the same $N$ and
expected degree $k$. A network is considered small-world when $\sigma > 1$,
meaning it is simultaneously more clustered *and* no longer than a random
graph of the same size.

In practice, $C_{\text{rand}} \approx k/N$ and $L_{\text{rand}} \approx \log N / \log k$,
so $\sigma \gg 1$ for networks with tightly-knit local clusters connected by
a few long-range shortcuts — exactly the Watts–Strogatz regime.

!!! example "Try it"
    - [Case Study → Facebook Network](real_network.md) — $\sigma \approx 39$ for a real social network
    - [API → Real Network](api/real_network.md) — `smallworldness_sigma`

## Random walks

The simple random walk on $G$ is a Markov chain with transition matrix

$$
P_{ij} = \begin{cases} 1 / d_j & \text{if } (i, j) \in E \\ 0 & \text{otherwise.}\end{cases}
$$

Here column $j$ is the current node, so $P_{ij}$ is the probability of
moving **from** $j$ **to** $i$. With this convention $P$ is
*column-stochastic* and the distribution evolves as
$\mathbf{p}_{t+1} = P\,\mathbf{p}_t$ — exactly as implemented in
`build_transition_matrix`.

On a connected, non-bipartite graph the unique stationary distribution
is

$$
\pi_i = \frac{d_i}{2m},
$$

which reduces to the uniform distribution when every node has the same
degree (exactly for the ring lattice, approximately for Watts–Strogatz).

!!! example "Try it"
    - [Explore → Random walk](explore/random_walk.md) — watch a walker traverse all three networks
    - [API → Simulation](api/simulation.md) — `random_walk`, `stationary_distribution`

### Characteristic times

**Cover time.** Expected number of steps until every node has been
visited at least once. Theoretically, on the ring it scales as
$\Theta(N^2)$; on a random regular graph it is $\Theta(N \log N)$.

**Mixing time.** Time for the walker's distribution to converge (in
total variation) to $\pi$:

$$
t_{\text{mix}}(\varepsilon) = \min \{ t : \max_i \| P^t(i, \cdot) - \pi \|_{\text{TV}} \le \varepsilon \}.
$$

It is governed by the **spectral gap** $1 - |\lambda_2|$ of $P$, where
$\lambda_2$ is the second-largest eigenvalue in absolute value. A
small spectral gap implies slow mixing.

The take-home result: the small-world network has **both** times
dramatically smaller than the ring lattice. A handful of random
shortcuts is enough to make diffusion fast.

!!! example "Try it"
    - [Explore → Cover time](explore/cover_time.md#cover-time) — Monte-Carlo cover time distribution
    - [Explore → Side-by-side: effect of β](explore/cover_time.md#side-by-side-effect-of-beta) — compare ring, WS, ER
    - [API → Simulation](api/simulation.md) — `cover_time`, `mixing_time`

## References

- D. J. Watts and S. H. Strogatz. *Collective dynamics of "small-world" networks*. Nature **393**, 440–442 (1998).
- S. Milgram. *The small-world problem*. Psychology Today **1**, 61–67 (1967).
- D. Levin and Y. Peres. *Markov chains and mixing times* (2nd ed.), AMS (2017).
- M. D. Humphries and K. Gurney. *Network 'small-world-ness': a quantitative method for determining canonical network equivalence*. PLOS ONE **3**(4), e0002051 (2008).
