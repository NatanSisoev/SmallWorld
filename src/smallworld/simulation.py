"""Defines the needed functions to make the simulations
"""
import networkx as nx
import numpy as np
from src.smallworld.networks import build_all                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
import src.smallworld.networks 


def random_walk_step(G: nx.Graph, current_node: int) -> int:
    """Take a random step from the current node to one of its neighbours."""
    return np.random.choice(
        list(G.neighbors(current_node))
    )
    
def random_walk(G: nx.Graph, start: int, n_steps: int) -> list[int]:
    """Simulates n_steps steps. Returns list of all visited nodes."""
    trace = []
    current_node = start
    for step in range(n_steps):
        next_node = random_walk_step(G, current_node=current_node)
        print(f"step:{step}: {current_node}->{next_node}")
        trace.append(next_node)
        current_node = next_node
    
    return trace
        
def mixing_time(G: nx.Graph) -> tuple[int, dict[int, float]]:
    """Calculate steps until convergence to the stationary distribution.
    Returns:
        tuple[int, dict[int, float]]: Number of steps to converge and the stationary distribution found.
    """
    
    
    
if __name__ == "__main__":

    N, k, beta = 50, 10, 0.1
    graphs = build_all(N=N, k=k, beta=beta, seed=42)
    G = graphs["ring"]
    
    # reproducibility
    seed = 42
    np.random.seed(seed=seed)
    root_node = np.random.choice(G.nodes)
    
    # FAST_TEST: random_step
    next_node = random_walk_step(G, current_node=root_node)
    print(f"\nNext node: {next_node}\n")
    
    # FAST_TEST: random_walk
    root_node = np.random.choice(G.nodes)
    trace = random_walk(G, start=root_node, n_steps=4)
    print(f"\nTrace: {trace}\n")