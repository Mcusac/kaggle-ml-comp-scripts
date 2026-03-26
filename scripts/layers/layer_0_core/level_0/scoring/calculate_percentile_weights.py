"""Percentile-based weight conversion for scored arrays."""

import numpy as np

from scipy.stats import rankdata


def calculate_percentile_weights(scores: np.ndarray) -> np.ndarray:
    """
    Convert an array of scores to percentile-based weights.

    Each element is replaced by its percentile rank within the array,
    expressed as a value in [0, 100].

    Args:
        scores: 1-D array of numeric scores.

    Returns:
        Float32 array of the same shape where each value is the percentile
        rank (0–100) of the corresponding score.
    """
    n = len(scores)
    ranks = rankdata(scores, method="average")
    return ((ranks - 1) / (n - 1) * 100.0).astype(np.float32) if n > 1 else np.full(n, 50.0, dtype=np.float32)