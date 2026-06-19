import numpy as np
from sklearn.metrics.pairwise import euclidean_distances

def create_adjacency_matrix(coords, threshold=0.05):
    dist_matrix = euclidean_distances(coords)
    adj = (dist_matrix < threshold).astype(float)
    np.fill_diagonal(adj, 1)
    return adj

def normalize_adj(adj):
    D = np.diag(np.sum(adj, axis=1))
    D_inv_sqrt = np.linalg.inv(np.sqrt(D))
    return D_inv_sqrt @ adj @ D_inv_sqrt