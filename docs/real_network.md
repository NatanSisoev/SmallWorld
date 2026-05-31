# Real-world case study: Facebook Social Network

## Objective

The rest of the project works with **synthetic networks** (ring, ER,
Watts–Strogatz) that we construct ourselves. Here we reverse the
direction: we take a **real network** and check whether it fits the
theory.

Two questions guide this section:

1. Is the Facebook friendship network truly *small-world*, or only appears
   so?
2. If it is, **which Watts–Strogatz model reproduces it** — that is,
   at what rewiring probability $\beta$ would a regular network acquire
   the same properties as Facebook?

The underlying intuition: a social network should have tightly-knit
communities (your friends know each other → high clustering) yet also
connect distant people in few hops (the *six degrees of separation*
→ short paths). This is exactly the small-world regime.

---

## The dataset

**Facebook Social Circles** (McAuley & Leskovec, NIPS 2012), published by
[SNAP](https://snap.stanford.edu/data/ego-Facebook.html): anonymised
real-world ego-network friendships.

| Property | Value |
|---|---|
| Nodes | 4,039 |
| Edges | 88,234 |
| Average degree $\langle k \rangle$ | ~44 |
| Clustering coefficient $C$ | ~0.61 |
| Average path length $L$ | ~3.73 |
| Diameter | 8 |
| Connected | yes |

It is connected and undirected, so it fits directly with everything we've
built for synthetic networks.

---

## What we found

### Is it small-world? — Yes, decisively

The smallworldness coefficient (defined and explained on the
[Theory page](theory.md)) compares the network to an equivalent random
graph. A value $\sigma > 1$ already indicates small-world behaviour.

For Facebook we obtain **σ ≈ 39**, an enormous value. The intuition:
the network has roughly **56 times more clustering** than a random
graph of the same size, yet its paths are only **40% longer**.
It has strong local structure without sacrificing short paths —
the hallmark of small-world networks.

### Which Watts–Strogatz reproduces it? — β ≈ 0.05

Searching for the $\text{WS}(N, k, \beta)$ model that best reproduces
both metrics simultaneously, the best fit is **β\* ≈ 0.052**: by
rewiring only about **5% of the edges** in a regular network,
we can recreate Facebook's properties.

This value falls squarely within the **small-world window**
($\beta \in [10^{-2}, 10^{-1}]$) that we study in
[Theory → The small-world window](theory.md#the-small-world-window).
It is the key result of this section: a real social network lives
exactly in the regime the Watts–Strogatz model predicts as interesting.

---

## The visualisation

<iframe src="../examples/facebook_analysis.html" width="100%" scrolling="no"
  style="height:420px;border:1px solid #e0e0e0;border-radius:6px;display:block"></iframe>

**Left panel — the fit.** The two solid curves show how $L$ (blue) and
$C$ (red), normalised, change as we increase $\beta$ from a regular
network ($\beta\to0$) to a random one ($\beta\to1$). The dashed lines
are Facebook's actual values. Where the two curves simultaneously approach
their corresponding Facebook lines gives the best imitation: the vertical
green line marks this $\beta^*$. Notice that $L$ drops much faster than
$C$ — this is why there exists a window where a network can be both
highly clustered and have short paths.

**Right panel — why σ is so large.** It decomposes the coefficient into
its two ratios. The clustering bar ($C/C_{\text{rand}}$) is enormous
while the path-length bar ($L/L_{\text{rand}}$) is close to 1;
their ratio gives σ ≈ 39.

---

## Conclusions

Facebook's friendship network is not merely *suspected* to be small-world:
it is demonstrably small-world (σ ≈ 39), and moreover, is equivalent to a
Watts–Strogatz model with modest rewiring (β ≈ 0.05). This validates the
model outside the lab: the same mechanism that makes our synthetic networks
small-world — a few long-range links on a tightly-clustered base — is what
structures a real social network.

---

## Beyond Watts–Strogatz: what the model misses

The Watts–Strogatz model captures one crucial property of Facebook — short
paths with high clustering — but it leaves important aspects of the real
network unexplained.

### The degree distribution problem

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

### Preferential attachment: the growth mechanism

Why do real networks develop hubs? Preferential attachment offers an answer:
when a new node joins the network, it connects preferentially to nodes that
are already highly connected. This "rich-get-richer" mechanism is the basis of
the **Barabási–Albert** model (1999), which grows a network dynamically and
produces power-law degree distributions.

Watts–Strogatz, by contrast, is static: we build the network all at once
with a fixed number of nodes. There is no growth, no preferential attachment,
and no mechanism to create hubs.

### What Facebook really is

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

---

## Reference

> McAuley, J. & Leskovec, J. (2012).
> *Learning to Discover Social Circles in Ego Networks.*
> Advances in Neural Information Processing Systems (NIPS).
