import numpy as np
from permute_utils import permute_mod
from shuffle_utils import shuffled

def mod_single(dataset, mod_func, descriptor, i, keep_key=False, inputs_only=False):
    queries = {}
    replies = {}
    keys = []
    for k0 in dataset.keys:
        desc = (('copy{i}' if mod_func is np.copy else mod_func.__name__) 
                if descriptor is None else descriptor if isinstance(descriptor, str) 
                else descriptor(dataset.queries[k0])).format(i=i)
        func = lambda a, d: np.asarray(mod_func(a) if descriptor is None else mod_func(a, d)).tolist()
        k1 = k0 if keep_key else f"{k0}.{'I' if inputs_only else ''}{desc}"
        keys.append(k1)
        queries[k1] = {m: [{t: (func(a, desc) if t=='input' or not inputs_only else a) 
                            for t, a in x.items()} for x in e] 
                       for m, e in dataset.queries[k0].items()}
        if k0 in dataset.replies:
            replies[k1] = [func(a, desc) for a in dataset.replies[k0]]
    return dataset.__class__(queries=queries, replies=replies, keys=keys)

def mod(dataset, mod_func, descriptor=None, n=1, stack=None, keep=False, keep_key=False, shuffle=False, join=True, inputs_only=False):
    cur = dataset
    ret = [cur.shuffled() if shuffle else cur] if keep else []
    if stack is None: stack = mod_func.__name__.startswith('rot')
    for i in range(n):
        cur = (cur if stack else dataset).mod_single(mod_func, descriptor, i=i, keep_key=keep_key, inputs_only=inputs_only)
        ret.append(cur.shuffled() if shuffle else cur)
    return dataset.__class__.append(*ret) if join else ret