# Simulation

## Cover time

The **cover time** $C(G)$ of a graph $G$ is the expected number of steps a
random walk needs to visit every node at least once, starting from the
worst-case initial node.  It captures how efficiently a walk can explore the
whole network.

For a $d$-regular graph on $N$ nodes the cover time scales roughly as:

$$
C(G) \;\sim\; \frac{2|E|}{d}\,H_N \;\approx\; N \ln N
$$

where $H_N$ is the $N$-th harmonic number.  In practice the constant depends
heavily on the graph structure:

| Graph | Expected scaling |
|---|---|
| Ring lattice | $\Theta(N^2)$ — the walker must traverse the whole ring |
| Erdős–Rényi | $\Theta(N \log N)$ — short paths reduce exploration time |
| Watts–Strogatz | $\Theta(N \log N)$ — shortcuts mimic the ER behaviour |

Use the interactive panels below to see this empirically.  Set the number of
simulations and click **▶ Run** — each simulation starts from a random node
and counts steps until every node has been visited at least once.

!!! note "How these are generated"
    The HTML files are produced by
    [`scripts/build_examples.py`](https://github.com/), which calls
    `src.smallworld.networks.build_all` followed by
    `src.smallworld.visualization.save_cover_time_visualization`.
    Both `make docs` and `make docs-serve` regenerate them automatically.
    All three networks use the same parameters: $N = 30$, $k = 4$,
    $\beta = 0.1$ (WS only), seed = 42.

---

## Ring lattice

Every node has degree $k = 4$, connected only to its nearest neighbours.
The walker is essentially trapped on a line, so cover time grows as $O(N^2)$.

<iframe src="../examples/cover_ring.html" width="100%" height="460" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

---

## Erdős–Rényi

Edges sampled independently with $p = k/(N-1)$.  Random shortcuts mean
short paths exist everywhere, giving much faster cover times.

<iframe src="../examples/cover_er.html" width="100%" height="460" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

---

## Watts–Strogatz ($\beta = 0.1$)

Start from the ring and rewire each edge with probability $\beta = 0.1$.
A handful of long-range shortcuts dramatically reduce the cover time
relative to the pure ring, approaching the Erdős–Rényi scaling.

<iframe src="../examples/cover_ws.html" width="100%" height="460" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

---

## Mixing time

The **mixing time** $t_{\text{mix}}(\varepsilon)$ of a random walk on a graph
$G$ measures how many steps it takes for the walk's probability distribution to
become indistinguishable (within tolerance $\varepsilon$) from the **stationary
distribution** $\pi$.

For a random walk on an undirected graph the stationary distribution is

$$
\pi(v) = \frac{\deg(v)}{2|E|}
$$

which is uniform for $k$-regular graphs.  Convergence is tracked via the
$\ell^\infty$ norm between consecutive distributions:

$$
t_{\text{mix}} = \min\bigl\{t : \|\mathbf{p}_{t} - \mathbf{p}_{t+1}\|_{\infty} < \varepsilon\bigr\}
$$

Equivalently, the mixing time is controlled by the **spectral gap**
$\lambda = 1 - \lambda_2(P)$ of the transition matrix $P$:

$$
t_{\text{mix}}(\varepsilon) \;\sim\; \frac{\ln(1/\varepsilon)}{\lambda}
$$

A larger spectral gap $\Rightarrow$ faster mixing.

| Graph | Mixing time scaling |
|---|---|
| Ring lattice | $\Theta(N^2)$ — small spectral gap, slow convergence |
| Erdős–Rényi | $\Theta(\log N)$ — large spectral gap, fast convergence |
| Watts–Strogatz | $\Theta(\log N)$ — shortcuts enlarge the spectral gap |

The simulation starts from a random initial distribution $\mathbf{p}_0$ (drawn
uniformly and normalised), multiplies by the transition matrix at each step, and
stops when consecutive distributions differ by less than `tol` in the
$\ell^\infty$ norm.  Results are averaged over `n_simulations` independent
runs.

---

## Interactive comparison: effect of $\beta$

The panel below lets you **directly compare** cover time and mixing time across
the three graph types for any choice of parameters.

1. Adjust $N$, $k$, $\beta$, and the number of simulations.
2. Click **▶ Run** to see a side-by-side bar chart and summary table for a
   single value of $\beta$.
3. Click **↻ Sweep β** to trace how both metrics change as $\beta$ sweeps from
   0.001 (almost a pure ring) to 0.7 (highly random) — with the ring and
   Erdős–Rényi values drawn as dashed reference lines.

!!! tip "What to look for"
    Already at $\beta \approx 0.01$–$0.1$ the Watts–Strogatz graph achieves
    cover and mixing times **close to the Erdős–Rényi reference**, while still
    keeping the high clustering of the regular ring.  This is the
    **small-world window**: a few random shortcuts are enough to dramatically
    speed up exploration of the network.

<iframe
  src="../examples/compare_times.html"
  width="100%"
  height="520"
  style="border: 1px solid #ddd; border-radius: 4px; overflow: hidden;">
</iframe>
