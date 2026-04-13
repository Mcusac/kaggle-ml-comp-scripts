import numpy as np

def shuffled(data_list):
    """Return a shuffled copy of a list."""
    return np.random.permutation(data_list).tolist()