"""Defines the functions needed to run the simulations."""
import networkx as nx
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from src.smallworld.networks import build_all

# ============================= Basic functionalities =============================
def random_walk_step(G: nx.Graph, current_node: int) -> int:
    """Take a random step from the current node to one of its neighbors."""
    return np.random.choice(
        list(G.neighbors(current_node))
    )
    
def random_walk(G: nx.Graph, start: int, n_steps: int) -> list[int]:
    """Simulate n_steps random-walk steps and return the visited nodes."""
    trace = []
    current_node = start
    for step in range(n_steps):
        next_node = random_walk_step(G, current_node=current_node)
        print(f"step:{step}: {current_node}->{next_node}")
        trace.append(next_node)
        current_node = next_node
    
    return trace


# ============================= Algorithms: Cover time and Mixing Time =============================
def _find_isolated_nodes(G: nx.Graph) -> list[int]:
    return list(nx.isolates(G=G))


def cover_time(G: nx.Graph, n_simulations: int, seed: int = None, max_iter: int = 100000) -> tuple[list[int], float]:
    """Calculate the average steps across the given simulations.
    Returns:
        tuple[list[int], np.float64]: Number of steps to visit all nodes for each simulation and the average number of steps."""
    
    
    isolated_nodes = _find_isolated_nodes(G=G)    
    all_nodes = list(G.nodes)
    
    # check whether there are isolated nodes
    if isolated_nodes:
        print("There are some isolated nodes:")
        print(isolated_nodes)
        print("\nCalculating cover time without isolated nodes...")
        all_nodes = list(set(all_nodes) - set(isolated_nodes))
        
    num_steps = []
    
    if seed is not None:
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
                num_steps.append(iter + 1)
                break
            
            current_node = next_node
            iter += 1
            
        if iter >= max_iter:
            return num_steps, np.inf # one of the simulations has not converged
    
    return num_steps, np.average(num_steps)
            
        
def mixing_time(G: nx.Graph, 
                n_simulations: int, 
                seed: int | None = None, 
                tol: float = 1e-5, 
                max_iter: int = 10000
) -> tuple[dict[int, dict[str, int | npt.NDArray[np.float64]]], float]:
    
    """Calculate average steps until convergence to the stationary distribution.
    Returns:
        tuple[int, dict[int, float]]: Number of steps to converge and the stationary distribution found.
    """
    P_mat, dim = build_transition_matrix(G=G)
    
    # reproducibility
    if seed is not None:
        np.random.seed(seed)
    
    out_dic = {}
    for sim in range(n_simulations):
        
        # probability distribution at time t=0
        root_vec = np.random.uniform(size=dim)
        root_vec = root_vec / root_vec.sum() # normalize vector
        
        original_vec = root_vec
        for iter in range(max_iter):
            next_vec = P_mat @ original_vec
            
            if np.max(np.abs(original_vec - next_vec)) < tol:
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
    """Calculate the transition matrix of the given graph."""

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


# ============================= Plots =============================
def plot_cover_time(steps_by_sim: list[int], name_graph: str = None):
    """Plots histogram of a given list of integers, representing the number of steps required for 
    the n-th simulation to have visited, at least once, all nodes of a graph"""
    
    steps_arr = np.array(steps_by_sim)
    vals_unique = np.unique(steps_arr, sorted=True)
    plt.figure(figsize=(10,6))
    plt.hist(x=steps_arr, bins=len(vals_unique), color="skyblue", edgecolor="black")
    
    plt.xlabel("Number of steps")    
    plt.ylabel("Frequency")
    if name_graph:
        plt.title(f"Histogram - Cover Time for {name_graph}", fontsize=14, fontweight="bold")    
    else: 
        plt.title("Histogram - Cover Time", fontsize=14, fontweight="bold")
    
    step = max(1, int(vals_unique[-1] / 20))
    ticks = np.arange(0, vals_unique[-1], step=step) # last element is the biggest one
    plt.xticks(ticks=ticks)
    
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()
        
def plot_mixing_time_distribution(prob_distribution: npt.NDArray[np.float64], name_graph: str = None):
    """Receive one probability distribution or several distributions from different simulations."""
    
    if not isinstance(prob_distribution[0], np.float64):
        prob_distribution = np.average(prob_distribution, axis=0) # average across simulations
        
    x_axis = np.arange(len(prob_distribution))
    y_axis = prob_distribution

    plt.figure(figsize=(8, 4.5))

    plt.bar(x_axis, y_axis, width=0.75, edgecolor="black", linewidth=0.8, alpha=0.85)

    plt.xlabel("Nodes", fontsize=12)
    plt.ylabel(r"$P(X = i)$", fontsize=12)
    if name_graph:
        plt.title(f"Mixing Time Probability Distribution for Graph: {name_graph}", fontsize=14, fontweight="bold")
    else:
        plt.title("Mixing Time Probability Distribution", fontsize=14, fontweight="bold")
    plt.xticks(x_axis)
    plt.ylim(0, max(y_axis) * 1.15)

    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()