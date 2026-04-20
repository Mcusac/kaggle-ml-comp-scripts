"""ARC color-channel permutation helpers (numpy)."""

import numpy as np


def permute_mod(a, descriptor, invert=False):
    permutation = [int(i) for i in descriptor if str(i).isdigit()]
    assert sorted(permutation) == list(range(10))

    a = np.asarray(a)

    if a.ndim == 3:
        if not invert:
            permutation = np.argsort(permutation)
        a = a[..., permutation]
    else:
        assert a.ndim == 2
        if invert:
            permutation = np.argsort(permutation)
        a = np.asarray(permutation)[a]

    return a


def permute_rnd_all_(query):
    permutation = np.random.permutation(10).tolist()
    return "permute" + "".join(map(str, permutation))
