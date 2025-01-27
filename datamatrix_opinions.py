import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx
from utils import get_graphs

def compute_neighbor_similarity(graph):
    """
    Computes the average similarity of opinions between neighbors in the graph.

    Args:
        graph (networkx.Graph): The graph with 'opinion' as a node attribute.

    Returns:
        float: Average similarity of opinions between neighbors.
    """
    total_similarity = 0
    total_edges = 0

    for node in graph.nodes():
        for neighbor in graph.neighbors(node):
            opinion_node = graph.nodes[node]['opinion']
            opinion_neighbor = graph.nodes[neighbor]['opinion']
            total_similarity += 1 - abs(opinion_node - opinion_neighbor)  # Similarity is 1 - distance
            total_edges += 1

    if total_edges == 0:  # Avoid division by zero
        return 0

    return total_similarity / total_edges

def analyze_neighbor_similarity(N_runs, N_nodes, time_steps, mu, epsilon_values):
    """
    Analyzes and calculates the average neighbor similarity for a range of epsilon values.

    Args:
        N_runs (int): Number of runs for each epsilon value.
        N_nodes (int): Number of nodes in the graph.
        time_steps (int): Number of time steps in the simulation.
        mu (float): Parameter for adjusting opinions.
        epsilon_values (list or numpy.ndarray): Range of epsilon values to test.

    Returns:
        list: Average neighbor similarity values for each epsilon value.
    """
    avg_similarities = []

    for epsilon in epsilon_values:
        print(f"Analyzing neighbor similarity for epsilon = {epsilon:.3f}")
        total_similarity = 0

        # Generate graphs for the given epsilon
        final_graphs, _ = get_graphs(N_runs, N_nodes, time_steps, epsilon, mu)

        # Calculate neighbor similarity for each graph and accumulate the total
        for graph in final_graphs:
            total_similarity += compute_neighbor_similarity(graph)

        # Compute the average similarity for this epsilon
        avg_similarity = total_similarity / N_runs
        avg_similarities.append(avg_similarity)

    return avg_similarities

def plot_neighbor_similarity(epsilon_values, similarities):
    """
    Plots the neighbor similarity as a function of epsilon.

    Args:
        epsilon_values (list or numpy.ndarray): Epsilon values (x-axis).
        similarities (list): Neighbor similarity values (y-axis).
    """
    plt.figure(figsize=(10, 6))
    plt.plot(epsilon_values, similarities, marker='o', linestyle='-', color='b', label='Neighbor Similarity')
    plt.xlabel('Epsilon')
    plt.ylabel('Average Neighbor Similarity')
    plt.title('Neighbor Similarity vs Epsilon')
    plt.grid(True)
    plt.legend()
    plt.show()

def opinion_matrix_experiment(N_runs, N_nodes, time_steps, mu_values, epsilon_values, output_file):
    """
    Investigates the average neighbor similarity by varying both epsilon and mu.
    Saves results as a 51x51 matrix to a CSV file.

    Args:
        N_runs (int): Number of simulation runs per parameter combination.
        N_nodes (int): Number of nodes in the graph.
        time_steps (int): Number of time steps for each simulation.
        mu_values (list or np.ndarray): Values of mu to investigate.
        epsilon_values (list or np.ndarray): Values of epsilon to investigate.
        output_file (str): File path to save the CSV results.
    """
    results_matrix = np.zeros((len(mu_values), len(epsilon_values)))  # Initialize matrix

    for i, epsilon in enumerate(epsilon_values):  # Outer loop: epsilon (horizontal)
        for j, mu in enumerate(mu_values):       # Inner loop: mu (vertical)
            print(f"Running simulation for epsilon={epsilon:.3f}, mu={mu:.3f}")
            # Analyze neighbor similarity
            avg_similarity = analyze_neighbor_similarity(N_runs, N_nodes, time_steps, mu, [epsilon])[0]
            results_matrix[j, i] = avg_similarity  # Store result in matrix

    # Save results to CSV
    df = pd.DataFrame(results_matrix, index=mu_values, columns=epsilon_values)
    df.to_csv(output_file)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    # Parameters
    N_RUNS = 5               # Number of runs per parameter combination
    N_NODES = 2000           # Number of nodes in each graph
    TIME_STEPS = 100         # Number of time steps per simulation
    MU_VALUES = np.linspace(0, 0.5, 51)       # 51 values for mu (0 to 0.5)
    EPSILON_VALUES = np.linspace(0, 0.5, 51)  # 51 values for epsilon (0 to 0.5)
    OUTPUT_FILE = "neighbor_opinion_similarity_matrix.csv"

    # Run the experiment
    opinion_matrix_experiment(N_RUNS, N_NODES, TIME_STEPS, MU_VALUES, EPSILON_VALUES, OUTPUT_FILE)
