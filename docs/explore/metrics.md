# Metric analytics

A single chart with a **dual y-axis** shows the **average path length**
$L$ (left axis, blue) and the **global clustering coefficient** $C$
(right axis, red) together, so the small-world window — where $L$ has
already dropped but $C$ is still high — is visible at a glance. All
values are computed on graphs with $N = 1000$ nodes (a single
realisation per $(k, \beta)$, fixed seed) using the hand-written
metrics from [`calculate_metrics.py`](../api/metrics.md).

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
    curve is still close to its ring value.

<iframe src="../../examples/metrics_analytics.html" width="100%" scrolling="no"
  style="height:72vh;min-height:500px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

!!! info "See also"
    - [Theory → The two metrics](../theory.md#the-two-metrics) — $L$ and $C$ definitions
    - [Theory → The small-world window](../theory.md#the-small-world-window) — why $L$ drops before $C$
    - [API → Metrics](../api/metrics.md) — `average_path_length`, `clustering_coefficient`
