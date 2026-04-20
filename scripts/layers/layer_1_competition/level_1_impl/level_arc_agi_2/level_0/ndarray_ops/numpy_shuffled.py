"""Deterministic numpy shuffle helper for ARC pipelines."""

import numpy as np


def shuffled(data_list):
    return np.random.permutation(data_list).tolist()
