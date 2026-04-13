import numpy as np
from arc_modifiers import mod
from permute_utils import permute_mod, permute_rnd_all_

def augment(dataset, n=1, shfl_keys=False, seed=42):
    np.random.seed(seed)
    d = dataset
    d = mod(d, np.transpose, keep=True)
    d = mod(d, np.rot90, n=3, keep=True)
    d = mod(d, permute_mod, permute_rnd_all_, n=n, shuffle=shfl_keys, keep=False)
    # optional: shuffle training examples
    return d