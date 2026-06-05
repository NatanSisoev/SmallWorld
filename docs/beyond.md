# Beyond Watts–Strogatz

*This page continues the [Facebook Network](real_network.md) case study.
For the model's mathematical background see [Theory](theory.md).*

The Watts–Strogatz model captures one crucial property of Facebook — short
paths with high clustering — but it leaves important aspects of the real
network unexplained.

## The degree distribution problem

In Watts–Strogatz, every node starts with degree close to $k$ (from the
regular ring). Rewiring edges randomly shuffles the network topology, but
nodes remain roughly **equally connected**. A node's degree might fluctuate
slightly, but there are no very-high-degree nodes (hubs) and no very-low-degree
ones.

Real social networks like Facebook tell a different story. Some users are
**highly connected** (influencers, celebrities, people with many friends),
while others have few connections. This creates a **heterogeneous degree
distribution** that Watts–Strogatz cannot reproduce. Empirically, many
real networks follow a **power-law** distribution: $P(k) \sim k^{-\gamma}$,
meaning the probability of a node having degree $k$ decays as a power law.
Networks with this property are called **scale-free**.

## Preferential attachment: the growth mechanism

Why do real networks develop hubs? Preferential attachment offers an answer:
when a new node joins the network, it connects preferentially to nodes that
are already highly connected. This "rich-get-richer" mechanism is the basis of
the **Barabási–Albert** model (1999), which grows a network dynamically and
produces power-law degree distributions.

Watts–Strogatz, by contrast, is static: we build the network all at once
with a fixed number of nodes. There is no growth, no preferential attachment,
and no mechanism to create hubs.

## What Facebook really is

A more realistic model of Facebook would combine:

- **Small-world structure** from Watts–Strogatz (short paths, high clustering).
- **Power-law degree distribution** from preferential attachment (hubs,
  heterogeneous connectivity).
- **Growth dynamics** — networks evolve as users join and form friendships.

The Watts–Strogatz fit we computed ($\beta^* \approx 0.052$) succeeds at
capturing the path-length and clustering trade-off. But it implicitly assumes
all nodes have comparable importance. In reality, Facebook's graph is more
nuanced: a small fraction of highly-followed accounts, a long tail of
casual users, and the interplay between local clustering and global hubs.

This is a reminder that all models are abstractions. Watts–Strogatz tells us
something true about social networks — that a small amount of disorder unlocks
short paths — but it is not the whole story.
