# The three networks

All three networks share the same $N$ and $k$, so their differences
are purely structural. Drag nodes, zoom, and hover to inspect IDs.

=== "Ring lattice"

    Every node connects to its $k/2 = 2$ nearest neighbours on each side.
    Maximally regular: high clustering, but the diameter grows linearly with $N$.

    <iframe src="../../examples/ring.html" width="100%" scrolling="no"
      style="height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Erdős–Rényi"

    Each pair of nodes is independently connected with probability $p = k/(N-1)$.
    No spatial structure: clustering near zero, but paths are short ($L \sim \log N / \log k$).

    <iframe src="../../examples/er.html" width="100%" scrolling="no"
      style="height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Watts–Strogatz ($\beta = 0.1$)"

    Start from the ring and rewire each edge with probability $\beta = 0.1$.
    A handful of shortcuts collapse the diameter while preserving most of the
    local clustering — the **small-world regime**.

    <iframe src="../../examples/ws.html" width="100%" scrolling="no"
      style="height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

!!! info "See also"
    - [Theory → The three networks](../theory.md#the-three-networks) — construction rules and expected metrics
    - [API → Networks](../api/networks.md) — `build_ring`, `build_er`, `build_ws`
