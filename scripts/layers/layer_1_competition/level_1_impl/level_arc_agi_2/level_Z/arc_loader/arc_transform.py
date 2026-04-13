import numpy as np
from permute_utils import permute_mod

def forward_mod(a, key, use_perm=True):
    if a is None: return a
    for op in key.split('.')[1:]:
        if   op == 'rot90':              a = np.rot90(a)
        elif op == 'transpose':          a = np.swapaxes(a, 0, 1)
        elif op.startswith('permute'):   a = permute_mod(a, op, invert=False) if use_perm else a
        elif op.startswith('copy'):      a = np.copy(a)
        elif op.startswith('out'):       a = a
        elif op.startswith('ex'):        a = a
        elif op.startswith('run'):       a = a
        else: raise NotImplementedError(f"Inversion of operation '{op}' unknown.")
    return a

def invert_mod(a, key, inv_perm=True):
    if a is None: return a
    for op in key.split('.')[1:][::-1]:
        if   op == 'rot90':              a = np.rot90(a, k=3)
        elif op == 'transpose':          a = np.swapaxes(a, 0, 1)
        elif op.startswith('permute'):   a = permute_mod(a, op, invert=True) if inv_perm else a
        elif op.startswith('copy'):      a = np.copy(a)
        elif op.startswith('out'):       a = a
        elif op.startswith('ex'):        a = a
        elif op.startswith('run'):       a = a
        else: raise NotImplementedError(f"Inversion of operation '{op}' unknown.")
    return a