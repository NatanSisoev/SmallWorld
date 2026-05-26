# Interactive examples

The three reference networks rendered with
[pyvis](https://pyvis.readthedocs.io/). **Drag nodes, zoom, and hover**
to see node IDs.

All three networks are built with the same parameters: $N = 30$,
$k = 4$, and (for the Watts–Strogatz graph) $\beta = 0.1$. The code is
identical to the one used in
[`notebooks/01_visualise_networks.ipynb`](https://github.com/) — see
the [API reference](api/networks.md) for the underlying functions.

!!! note "How these are generated"
    The HTML files are produced by
    [`scripts/build_examples.py`](https://github.com/), which calls
    `src.smallworld.networks.build_all` followed by
    `src.smallworld.plotting.to_pyvis` + `save_pyvis`. Both
    `make docs` and `make docs-serve` regenerate them automatically.

## Ring lattice

Every node is connected to its $k/2 = 2$ neighbours on each side.
**Highly clustered**, but the path length grows linearly with $N$ —
to reach the antipode you walk around half the ring.

<iframe src="ring.html" width="100%" height="520" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Erdős–Rényi

Each edge sampled independently with $p = k / (N - 1)$. **No spatial
structure**; clustering vanishes for large $N$ but paths are short
($L \sim \log N / \log k$).

<iframe src="er.html" width="100%" height="520" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

## Watts–Strogatz ($\beta = 0.1$)

Start from the ring and rewire each edge with probability $\beta$. A
few chords across the circle are visible — **those are the shortcuts**
that collapse the diameter while preserving most of the local
clustering.

<iframe src="ws.html" width="100%" height="520" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

---

## Random walk

Interactive random-walk simulation on each of the three networks.
The walker starts at node **0** (green). Use the controls to advance
the walk step by step or let it run automatically.

**Controls:**

- **▶ Step** — one step at a time.
- **▶▶ Walk N** — jump *N* steps at once (edit the *N* field).
- **⏵ Auto** — animated playback; edit the *ms* field to set the
  speed (milliseconds per step). Click again to pause.
- **↺ Reset** — restart from node 0.
- **Click a node** — restart the walk from that node.

**Colour key:** green = start · red = current · orange = visited · blue = unvisited.

!!! note "How these are generated"
    The HTML files are produced by
    [`scripts/build_examples.py`](https://github.com/), which calls
    `src.smallworld.networks.build_all` followed by
    `src.smallworld.visualization.save_walk_visualization`.
    Both `make docs` and `make docs-serve` regenerate them automatically.

### Ring lattice

<iframe src="walk_ring.html" width="100%" height="640" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

### Erdős–Rényi

<iframe src="walk_er.html" width="100%" height="640" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>

### Watts–Strogatz ($\beta = 0.1$)

<iframe src="walk_ws.html" width="100%" height="640" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>
