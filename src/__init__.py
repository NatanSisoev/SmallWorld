"""SmallWorld - library code for the small-world course project.

Two submodules are provided:

* :mod:`src.networks` - builders for the three reference networks: a
  regular ring lattice, an Erdős-Rényi random graph, and a
  Watts-Strogatz small-world graph.
* :mod:`src.plotting` - visualisation helpers, both static
  (matplotlib, used for the report figures) and interactive (pyvis,
  exported as standalone HTML pages).

Forthcoming: ``metrics`` (average path length, clustering, β-sweep)
and ``walks`` (random-walk simulation, cover time, mixing time).

The numbered notebooks under ``notebooks/`` are the experiments that
consume this code; ``docs/index.md`` is the human-readable project
overview.
"""
