"""Defines the needed functions to make the simulations
"""
import networkx as nx
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from src.smallworld.networks import build_all

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

def cover_time(G: nx.Graph, n_simulations: int, seed: int = None, max_iter: int = 100000) -> tuple[list[int], np.float64]:
    """Calculate the average steps across the given simulations.
    Returns:
        tuple[list[int], np.float64]: Number of steps to visit all nodes for each simulation and the average number of steps."""
    
    all_nodes = list(G.nodes)
    num_steps = []
    
    if seed:
        np.random.seed(seed)
        
    for sim in range(n_simulations):
        current_node =  int(np.random.choice(all_nodes))
        to_visit = set(all_nodes)
        
        to_visit.discard(current_node)
        iter = 0
        
        while to_visit and (iter < max_iter):
            next_node = random_walk_step(G=G, current_node=current_node)
            to_visit.discard(next_node)
            
            if not to_visit:
                num_steps.append(iter)
                break
            
            current_node = next_node
            iter += 1
            
        if iter >= max_iter:
            return num_steps, np.inf # one of the simulations has not converged
    
    return num_steps, np.average(num_steps)
            
        
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

def plot_mixing_time_distribution(prob_distribution: npt.NDArray[np.float64], name_graph: str = None):
    """Receives an array of on distribution or an array of arrays of distributions across the different simulations"""
    
    if not isinstance(prob_distribution[0], np.float64):
        prob_distribution = np.average(prob_distribution, axis=0) # average across simulations
        
    x_axis = np.arange(len(prob_distribution))
    y_axis = prob_distribution

    plt.figure(figsize=(8, 4.5))

    plt.bar(x_axis, y_axis, width=0.75, edgecolor="black", linewidth=0.8, alpha=0.85)

    plt.xlabel("Nodes", fontsize=12)
    plt.ylabel(r"$P(X = \mathrm{node}_i)$", fontsize=12)
    if name_graph:
        plt.title(f"Mixing Time Probability Distribution for Graph: {name_graph}", fontsize=14, fontweight="bold")
    else:
        plt.title("Mixing Time Probability Distribution", fontsize=14, fontweight="bold")
    plt.xticks(x_axis)
    plt.ylim(0, max(y_axis) * 1.15)

    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()