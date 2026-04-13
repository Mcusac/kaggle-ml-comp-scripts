import numpy as np

def permute_mod(a, descriptor, invert=False):
    """Permute array according to descriptor string."""
    permutation = [int(i) for i in descriptor if str(i).isdigit()]
    assert sorted(permutation) == list(range(10)), f"Invalid permutation descriptor: {descriptor}"
    a = np.asarray(a)
    if a.ndim == 3:
        if not invert: permutation = np.argsort(permutation)
        a = a[..., permutation]
    elif a.ndim == 2:
        if invert: permutation = np.argsort(permutation)
        a = np.asarray(permutation)[a]
    else:
        raise ValueError(f"Unsupported array ndim {a.ndim}")
    return a

def permute_rnd_all_(_):
    """Return a random permutation descriptor string."""
    permutation = np.random.permutation(10).tolist()
    return 'permute' + ''.join(map(str, permutation))