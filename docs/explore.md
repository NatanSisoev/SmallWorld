# Explore

Hands-on demos for every concept on the [Theory](theory.md) page.
All static examples use $N = 30$ nodes and $k = 4$ average degree;
interactive panels let you change parameters in real time.

---

## The three networks

All three networks share the same $N$ and $k$, so their differences
are purely structural. Drag nodes, zoom, and hover to inspect IDs.
See [Theory → The three networks](theory.md#the-three-networks) for
the construction rules and expected metrics.

=== "Ring lattice"

    Every node connects to its $k/2 = 2$ nearest neighbours on each side.
    Maximally regular: high clustering, but the diameter grows linearly with $N$.

    <iframe src="../examples/ring.html" width="100%" scrolling="no"
      style="height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Erdős–Rényi"

    Each pair of nodes is independently connected with probability $p = k/(N-1)$.
    No spatial structure: clustering near zero, but paths are short ($L \sim \log N / \log k$).

    <iframe src="../examples/er.html" width="100%" scrolling="no"
      style="height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Watts–Strogatz ($\beta = 0.1$)"

    Start from the ring and rewire each edge with probability $\beta = 0.1$.
    A handful of shortcuts (drawn in orange) collapse the diameter while
    preserving most of the local clustering — the **small-world regime**.

    <iframe src="../examples/ws.html" width="100%" scrolling="no"
      style="height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

---

## Metric analytics

A single chart with a **dual y-axis** shows the **average path length**
$L$ (left axis, blue) and the **global clustering coefficient** $C$
(right axis, red) together, so the small-world window — where $L$ has
already dropped but $C$ is still high — is visible at a glance. All
values are computed on graphs with $N = 1000$ nodes (a single
realisation per $(k, \beta)$, fixed seed) using the hand-written
metrics from [`calculate_metrics.py`](../api/networks.md).

The $\beta$ axis sweeps the decade-spaced set
$\{10^{-4},\, 10^{-3},\, 10^{-2},\, 10^{-1},\, 1\}$, so the points are
equidistant on the log axis. The ring lattice (dashed) and Erdős–Rényi
(dotted) constants are drawn at their fixed values for both metrics —
they don't depend on $\beta$ — and the Watts–Strogatz curves (solid,
with markers) interpolate between them.

**Controls:**

- **k slider** — average degree, in steps of $10$ from $10$ to $100$
  neighbours. The chart redraws live as you slide.

!!! tip "What to look for"
    As $k$ grows, the ring's $L$ collapses (more direct connections),
    while $C$ stays near $3/4$ for any $k$. The Watts–Strogatz curves
    follow the ring at $\beta \to 0$ and the Erdős–Rényi limit at
    $\beta \to 1$; the small-world window is the range of $\beta$
    where the blue $L$ curve has already dropped but the red $C$
    curve is still close to its ring value. See
    [Theory → The small-world window](theory.md#the-small-world-window).

<iframe src="../examples/metrics_analytics.html" width="100%" scrolling="no"
  style="height:72vh;min-height:500px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

---

## Random walk

A walker moves to a uniformly chosen neighbour at every step. Colour
tracks the state: **green** = start, **red** = current position,
**orange** = already visited, **blue** = not yet reached.

Click any node to restart the walk from there.
See [Theory → Random walks](theory.md#random-walks) for the Markov
chain formulation and stationary distribution.

=== "Ring lattice"

    The walker is trapped near its starting point for a long time —
    there are no shortcuts, so spreading across the ring is slow.

    <iframe src="../examples/walk_ring.html" width="100%" scrolling="no"
      style="height:70vh;min-height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Erdős–Rényi"

    Random structure means the walker can jump across the graph in just
    a few steps — coverage is very fast but the graph has no spatial order.

    <iframe src="../examples/walk_er.html" width="100%" scrolling="no"
      style="height:70vh;min-height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Watts–Strogatz ($\beta = 0.1$)"

    The rewired shortcuts act as long-range teleporters. Watch how the
    walker occasionally jumps across the ring — these are exactly the edges
    that drive the small-world speedup.

    <iframe src="../examples/walk_ws.html" width="100%" scrolling="no"
      style="height:70vh;min-height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

---

## Cover time

The **cover time** is the expected number of steps to visit every node
at least once. Set the number of simulations and click **▶ Run** to
see the distribution. Compare the histograms across the three networks
— the ring takes roughly $\Theta(N^2)$ steps, the other two
$\Theta(N \log N)$.

See [Theory → Characteristic times](theory.md#characteristic-times)
for the analytical scaling.

=== "Ring lattice"

    <iframe src="../examples/cover_ring.html" width="100%" scrolling="no"
      style="height:62vh;min-height:420px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Erdős–Rényi"

    <iframe src="../examples/cover_er.html" width="100%" scrolling="no"
      style="height:62vh;min-height:420px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Watts–Strogatz ($\beta = 0.1$)"

    <iframe src="../examples/cover_ws.html" width="100%" scrolling="no"
      style="height:62vh;min-height:420px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

---

## Side-by-side: effect of $\beta$

This panel runs all three graphs simultaneously so you can compare
cover time and mixing time directly. Use the $\beta$ slider to sweep
from the pure ring ($\beta \to 0$) to a fully random graph ($\beta = 1$)
and watch both metrics change.

!!! tip "What to look for"
    Already at $\beta \approx 0.01$–$0.1$, the Watts–Strogatz graph
    matches the Erdős–Rényi cover and mixing times while still showing
    the ring's high clustering. This is the **small-world window** — see
    [Theory → The small-world window](theory.md#the-small-world-window)
    for why $L$ and $C$ collapse at different scales.

**Controls:**

- **▶ Cover Time** — animated walks until every node is visited.
- **▶ Mixing Time** — matrix iteration to the stationary distribution
  $\pi(v) = \deg(v)/2|E|$; the bar chart below each panel shows $\pi$.
- **↺ Reset** — clear results and redraw the graphs.
- **$\beta$ slider** — updates the Watts–Strogatz graph live.

<iframe src="../examples/compare_times.html" width="100%" scrolling="no"
  style="height:80vh;min-height:520px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>
