''' Multiprocessing functions for generating dicts with data,
uses the combined analysis function in opynions.analysis.combined. '''

import multiprocessing as mp
import itertools
from opynions.analysis.combined import combined_analysis
from opynions.analysis.distribution import opinions_variance

def worker_all_both_params(epsilon, mu, n_runs, n_nodes, time_steps, m_ba):
        ''' 
        Process manager, receives all parameters needed 
        and returns a dict full of the combined analysis results for that parameter space point.
        '''
        results_dict = combined_analysis(n_runs, n_nodes, time_steps, epsilon, mu, m_ba)
        results_dict['epsilon'] = epsilon
        results_dict['mu'] = mu
        return results_dict

def multiprocess_all(epsilon_values, mu_values, n_runs, n_nodes, time_steps, m_ba):
    """
    Performs all the analysis types on the given parameters using multiprocessing.

    Parameters:
    epsilon_values (list): List of epsilon values to be used in the analysis.
    mu_values (list): List of mu values to be used in the analysis.
    n_runs (int): Number of runs for each parameter combination.
    n_nodes (int): Number of nodes in the network.
    time_steps (int): Number of time steps for the simulation.
    m_ba (int): affects graph generation, see networkx.barabasi_albert_graph()

    Returns:
    list: A list of dictionaries containing the results of the analysis for each parameter combination.
    """

    param_grid = list(itertools.product(epsilon_values, mu_values))
    num_workers = min(mp.cpu_count(), len(param_grid))
    with mp.Pool(num_workers) as pool:
        list_of_dicts = pool.starmap(worker_all_both_params, [(epsilon, mu, n_runs, n_nodes, time_steps, m_ba) for epsilon, mu in param_grid])

    return list_of_dicts

def worker_variance_epsilons(epsilon, m_ba):
    ''' Process manager for variance analysis used in finite size scaling analysis.'''
    variance = opinions_variance(10, 200, 100, epsilon, 0.48, m_ba=m_ba)
    return variance

def multiprocess_variance_epsilon(epsilon_values, m_ba):
    ''' Performs only variance analysis, to be used in finite size scaling analysis.'''
    num_workers = min(mp.cpu_count(), len(epsilon_values))
    with mp.Pool(num_workers) as pool:
        list_of_variances = pool.starmap(worker_variance_epsilons, [(epsilon, m_ba) for epsilon in epsilon_values])
    return list_of_variances