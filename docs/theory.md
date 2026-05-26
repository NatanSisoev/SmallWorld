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
    Drag, zoom, and hover each network interactively →
    [Explore → The three networks](explore.md#the-three-networks)

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

This is the *global* (or transitivity) definition. The *average
local* version — average over nodes of
$c_i = 2 \cdot e_i / [d_i(d_i - 1)]$ where $e_i$ is the number of
edges among $i$'s neighbours — is computed separately for comparison.
The original Watts–Strogatz paper uses average local.

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
    Sweep $\beta$ and watch $L$ and $C$ evolve in real time →
    [Explore → Side-by-side: effect of β](explore.md#side-by-side-effect-of-beta)

## Random walks

The simple random walk on $G$ is a Markov chain with transition matrix

$$
P_{ij} = \begin{cases} 1 / d_i & \text{if } (i, j) \in E \\ 0 & \text{otherwise.}\end{cases}
$$

On a connected, non-bipartite graph the unique stationary distribution
is

$$
\pi_i = \frac{d_i}{2m},
$$

which reduces to the uniform distribution when every node has the same
degree (exactly for the ring lattice, approximately for Watts–Strogatz).

!!! example "Try it"
    Watch a walker traverse all three networks step by step →
    [Explore → Random walk](explore.md#random-walk)

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
    Run Monte-Carlo cover-time and mixing-time simulations →
    [Explore → Cover time](explore.md#cover-time) ·
    [Explore → Side-by-side: effect of β](explore.md#side-by-side-effect-of-beta)

## References

- D. J. Watts and S. H. Strogatz. *Collective dynamics of "small-world" networks*. Nature **393**, 440–442 (1998).
- S. Milgram. *The small-world problem*. Psychology Today **1**, 61–67 (1967).
- D. Levin and Y. Peres. *Markov chains and mixing times* (2nd ed.), AMS (2017).
