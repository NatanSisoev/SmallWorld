# Random walk

A walker moves to a uniformly chosen neighbour at every step. Colour
tracks the state: **green** = start, **red** = current position,
**orange** = already visited, **blue** = not yet reached.

Click any node to restart the walk from there.

=== "Ring lattice"

    The walker is trapped near its starting point for a long time —
    there are no shortcuts, so spreading across the ring is slow.

    <iframe src="../../examples/walk_ring.html" width="100%" scrolling="no"
      style="height:70vh;min-height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Erdős–Rényi"

    Random structure means the walker can jump across the graph in just
    a few steps — coverage is very fast but the graph has no spatial order.

    <iframe src="../../examples/walk_er.html" width="100%" scrolling="no"
      style="height:70vh;min-height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

=== "Watts–Strogatz ($\beta = 0.1$)"

    The rewired shortcuts act as long-range teleporters. Watch how the
    walker occasionally jumps across the ring — these are exactly the edges
    that drive the small-world speedup.

    <iframe src="../../examples/walk_ws.html" width="100%" scrolling="no"
      style="height:70vh;min-height:480px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

!!! info "See also"
    - [Theory → Random walks](../theory.md#random-walks) — Markov chain formulation and stationary distribution
    - [API → Simulation](../api/simulation.md) — `random_walk`, `stationary_distribution`
