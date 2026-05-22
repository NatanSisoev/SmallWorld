"""Defines the functions needed to run the simulations."""
import networkx as nx
import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from src.smallworld.networks import build_all

# ============================= Basic functionalities =============================
def random_walk_step(G: nx.Graph, current_node: int) -> int:
    """Take a single random step from ``current_node`` to one of its neighbours.

    Parameters
    ----------
    G : networkx.Graph
        The graph on which to walk.
    current_node : int
        The node from which to step.

    Returns
    -------
    int
        A neighbour of ``current_node`` chosen uniformly at random.
    """
    return np.random.choice(
        list(G.neighbors(current_node))
    )
    
def random_walk(G: nx.Graph, start: int, n_steps: int) -> list[int]:
    """Simulate a random walk of ``n_steps`` steps starting from ``start``.

    Parameters
    ----------
    G : networkx.Graph
        The graph on which to walk.
    start : int
        Starting node.
    n_steps : int
        Number of steps to take.

    Returns
    -------
    list[int]
        Sequence of visited nodes (excluding the start), of length ``n_steps``.
    """
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
    """Estimate the cover time of ``G`` by Monte-Carlo simulation.

    The **cover time** $C(G)$ is the expected number of steps a random walk
    needs to visit every node at least once.  This function approximates it by
    averaging over many independent simulations, each started from a uniformly
    random non-isolated node.

    Empirical scaling laws:

    | Graph | Scaling |
    |---|---|
    | Ring lattice | $\\Theta(N^2)$ |
    | Erdős–Rényi / Watts–Strogatz | $\\Theta(N \\log N)$ |

    Parameters
    ----------
    G : networkx.Graph
        Graph to simulate on.  Isolated nodes are automatically excluded from
        both the start set and the set of nodes to visit.
    n_simulations : int
        Number of independent random walks to run.
    seed : int, optional
        Seed for :func:`numpy.random.seed` (``seed=0`` is supported).
    max_iter : int, default 100 000
        Hard step limit per simulation.  If a walk has not covered all nodes
        within ``max_iter`` steps, the function returns immediately with
        ``np.inf`` as the average.

    Returns
    -------
    num_steps : list[int]
        Number of steps taken in each successful simulation.
    avg : float or np.inf
        Mean cover time across all simulations, or ``np.inf`` if any run
        exceeded ``max_iter``.
    """
    
    
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
    """Estimate the mixing time of ``G`` by iterated matrix–vector products.

    The **mixing time** measures how many steps a random walk needs before its
    probability distribution is indistinguishable (within tolerance
    $\\varepsilon$) from the stationary distribution

    $$\\pi(v) = \\frac{\\deg(v)}{2|E|}$$

    Convergence is tracked via the $\\ell^\\infty$ norm between consecutive
    distributions:

    $$t_{\\mathrm{mix}} = \\min\\bigl\\{t : \\|\\mathbf{p}_t - \\mathbf{p}_{t+1}\\|_{\\infty} < \\varepsilon \\bigr\\}$$

    Each simulation starts from a different random initial distribution
    $\\mathbf{p}_0$ (drawn uniformly and normalised).

    Parameters
    ----------
    G : networkx.Graph
        Graph whose mixing time is to be estimated.
    n_simulations : int
        Number of independent runs (each uses a fresh random $\\mathbf{p}_0$).
    seed : int, optional
        Seed for :func:`numpy.random.seed` (``seed=0`` is supported).
    tol : float, default 1e-5
        Convergence tolerance $\\varepsilon$ for the $\\ell^\\infty$ norm.
    max_iter : int, default 10 000
        Maximum number of matrix–vector multiplications per simulation.

    Returns
    -------
    out_dic : dict[int, dict]
        Keyed by simulation index ``0 … n_simulations-1``.  Each entry is a
        dict with:

        - ``"iters"`` — number of iterations until convergence.
        - ``"distribution"`` — final probability vector, shape ``(N,)``.
    time_avg : float
        Average number of iterations across all converged simulations.
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
    """Build the column-stochastic transition matrix for a random walk on ``G``.

    Entry $P_{ij}$ is the probability of moving **from** node $j$ **to**
    node $i$ in one step:

    $$P_{ij} = \\begin{cases} 1/\\deg(j) & (i,j)\\in E \\\\ 0 & \\text{otherwise} \\end{cases}$$

    For a $k$-regular graph the stationary distribution is uniform:
    $\\pi(v) = 1/N$.

    Parameters
    ----------
    G : networkx.Graph
        An undirected, unweighted graph on $N$ nodes.

    Returns
    -------
    P_mat : numpy.ndarray, shape (N, N)
        Column-stochastic transition matrix.
    dim : int
        Number of nodes $N$.
    """

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
    """Plot a histogram of cover-time simulation results.

    Parameters
    ----------
    steps_by_sim : list[int]
        Raw output from :func:`cover_time` — number of steps for each
        successful simulation run.
    name_graph : str, optional
        Graph name used in the plot title.
    """
    
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
    """Plot the stationary-distribution estimate from a mixing-time run.

    Parameters
    ----------
    prob_distribution : numpy.ndarray
        Either a 1-D array of length $N$ (single distribution) or a 2-D array
        of shape ``(n_simulations, N)`` (one distribution per simulation).  In
        the latter case the distributions are averaged before plotting.
    name_graph : str, optional
        Graph name used in the plot title.
    """
    
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