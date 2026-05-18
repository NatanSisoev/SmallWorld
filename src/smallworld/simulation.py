"""Defines the needed functions to make the simulations
"""
import networkx as nx
import numpy as np
import numpy.typing as npt
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
        
def mixing_time(G: nx.Graph, n_simulations: int, seed: int = None, tol: float = 1e-5, max_iter: int = 10000) -> tuple[int, dict[int, float]]:
    """Calculate average steps until convergence to the stationary distribution.
    Returns:
        tuple[int, dict[int, float]]: Number of steps to converge and the stationary distribution found.
    """
    P_mat, dim = build_transition_matrix(G=G)
    
    # reproducibility
    if seed:
        np.random.seed(seed)
    
    out_dic = {}
    for sim in range(n_simulations):
        
        # probability distribution at time t=0
        root_vec = np.random.uniform(size=dim)
        root_vec = root_vec / root_vec.sum() # normalize vector
        
        original_vec = root_vec
        for iter in range(max_iter):
            next_vec = P_mat @ original_vec
            
            if np.max(original_vec - next_vec) < tol:
                # save info in dictionary
                out_dic[sim] = {
                    "iters": iter,
                    "distribution": next_vec
                }
                
                break
            
            original_vec = next_vec
            
    # compute average time until convergence
    time_avg = np.average([out_dic[sim]["iters"] for sim in out_dic])
     
    return out_dic, time_avg
    
def build_transition_matrix(G: nx.Graph) -> tuple[npt.NDArray[np.float64], int]:
    """Calculates the transition matrix of the given graph"""

    dim = G.number_of_nodes()
    P_mat = np.zeros((dim, dim), dtype=float)
    
    for node in G.nodes:
        neighbours = list(G.neighbors(node))
        total_nbs = len(neighbours)
        
        # assume uniform distribution
        P_mat[:, node] = np.array([ 1/total_nbs if i in neighbours else 0
                                   for i in range(dim)],
                                  dtype=float)
        
    return P_mat, dim

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
    
    # FAST_TEST: mixing_time
    _, time_average = mixing_time(G, 50)
    print(time_average)