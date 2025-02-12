''' Core model functions.
Refer to the paper for more details on the model: https://www.nature.com/articles/srep40391'''

import random
import networkx as nx
import matplotlib.pyplot as plt

def rho(x):
    '''Function used to guarantee periodic boundary conditions as per eq 1 in paper
    
    Args:
        x (float): opinion distance between two nodes, bounds [-1, 1]
    Returns:
        (int) -1, 0, or 1 based on x
    '''
    assert -1 <= x <= 1, f"x is out of bounds [-1, 1]: {x}"
    if -1 <= x < -0.5:
        return -1
    if -0.5 <= x <= 0.5:
        return 0
    if 0.5 < x <= 1:
        return 1

def UCM_adjust_opinion(i, j, mu, epsilon):
    '''Adjusts opinions i and j based on the given parameters as per eq 2 & 3 in paper
    
    Args:
        i (float): opinion i
        j (float): opinion j
        mu (float): parameter for adjusting opinions, bounds [0,1]
        epsilon (float): threshold for opinion distance, bounds [0,1]
    '''

    assert 0 <= i <= 1, f"Opinion i is out of bounds: {i}"
    assert 0 <= j <= 1, f"Opinion j is out of bounds: {j}"

    i_min_j = i - j
    alt_dist = i_min_j- rho(i - j)
    abs_alt_dist = abs(alt_dist)
    j_min_i = j - i

    if abs_alt_dist < epsilon:
        i_new = i + mu * j_min_i
        j_new = j + mu * i_min_j

    if abs_alt_dist >= epsilon:
        i_new = i - mu * (j_min_i - rho(j - i))
        j_new = j - mu * alt_dist

        # ensure i_new and j_new are within [0, 1] in case of extreme repulsion
        i_new = max(0, min(1, i_new))
        j_new = max(0, min(1, j_new))

    return i_new, j_new

def initialize_graph(N, m_ba=2):
    '''Creates a Scale-Free graph with N nodes and uniformly random opinions between 0 and 1
    
    Args:
        N (int): number of nodes
        m_ba (int): affects graph generation, see networkx.barabasi_albert_graph()
    Returns:
        g: networkx graph
    '''
    g = nx.barabasi_albert_graph(N, m_ba) 
    opinions = {node: random.uniform(0, 1) for node in g.nodes()} # uniformly random opinions [0,1]
    nx.set_node_attributes(g, opinions, 'opinion')
    return g

def run_sim(N, T, epsilon, mu, m_ba=2):
    '''Runs simulation until T time steps and returns the final graph.
    
    Args:
        N (int): number of nodes
        T (int): number of time steps
        mu (float): parameter for adjusting opinions, bounds [0,1]
        epsilon (float): threshold for opinion distance, bounds [0,1]
        m_ba (int): affects graph generation, see networkx.barabasi_albert_graph()
        
    Returns: 
        g (networkx.Graph): final graph
        g_init (networkx.Graph): initial graph
    '''
    assert N > 1 & isinstance(N, int), f"N has to be an integer greater than 1: {N}"
    assert T > 1 & isinstance(T, int), f"T has to be an integer greater than 1: {T}"
    assert 0 <= mu <= 1, f"mu out of bounds [0,1]: {mu}"
    assert 0 <= epsilon <= 1, f"epsilon out of bounds [0,1]: {epsilon}"

    g = initialize_graph(N, m_ba)
    g_init = g.copy()
    for t in range(T):
        # For each node in a random order
        nodes = list(g.nodes())
        random.shuffle(nodes)
        for node in nodes:
            # if node has neighbors (might have been cut off by someone)
            if list(g.neighbors(node)): 
                # pick a random neighbor 
                neighbor = random.choice(list(g.neighbors(node)))
                i = g.nodes[node]['opinion']
                j = g.nodes[neighbor]['opinion']

                # adjust opinions (or not, handled by the adjustment function)
                i_new, j_new = UCM_adjust_opinion(i, j, mu, epsilon)
                g.nodes[node]['opinion'] = i_new
                g.nodes[neighbor]['opinion'] = j_new

                # rewire if opinions are too far apart
                if abs(i_new - j_new) > epsilon:
                    new_neighbor = random.choice(list(g.nodes()))
                    # ensure new neighbor is not the same as the node itself.
                    while new_neighbor == node:
                        new_neighbor = random.choice(list(g.nodes()))
                    g.remove_edge(node, neighbor)
                    g.add_edge(node, new_neighbor)

    return g, g_init
