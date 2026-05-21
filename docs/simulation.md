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
