# Cover & mixing time

## Cover time

The **cover time** is the expected number of steps to visit every node
at least once. Set the number of simulations and click **▶ Run** to
see the distribution. Compare the histograms across the three networks
— the ring takes roughly $\Theta(N^2)$ steps, the other two
$\Theta(N \log N)$.


=== "Ring lattice"

    <iframe src="../../examples/cover_ring.html" width="100%" scrolling="no"
      style="height:62vh;min-height:420px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Erdős–Rényi"

    <iframe src="../../examples/cover_er.html" width="100%" scrolling="no"
      style="height:62vh;min-height:420px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Watts–Strogatz ($\beta = 0.1$)"

    <iframe src="../../examples/cover_ws.html" width="100%" scrolling="no"
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
    the ring's high clustering. This is the **small-world window** —
    the range where $L$ has collapsed but $C$ is still high.

**Controls:**

- **▶ Cover Time** — animated walks until every node is visited.
- **▶ Mixing Time** — matrix iteration to the stationary distribution
  $\pi(v) = \deg(v)/2|E|$; the bar chart below each panel shows $\pi$.
- **↺ Reset** — clear results and redraw the graphs.
- **$\beta$ slider** — updates the Watts–Strogatz graph live.

<iframe src="../../examples/compare_times.html" width="100%" scrolling="no"
  style="height:80vh;min-height:520px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

!!! info "See also"
    - [Theory → Characteristic times](../theory.md#characteristic-times) — analytical scaling of cover and mixing time
    - [Theory → The small-world window](../theory.md#the-small-world-window) — why $L$ and $C$ collapse at different $\beta$ scales
    - [API → Simulation](../api/simulation.md) — `cover_time`, `mixing_time`
