"""Weight manipulation helpers for ensemble methods."""

import numpy as np

from level_0 import DataValidationError

EPSILON_WEIGHT = 1e-6


def ensure_positive_weights(weights_array: np.ndarray) -> np.ndarray:
    """Ensure all weights are positive and non-zero."""
    weights = weights_array.copy()
    min_weight = np.min(weights)
    if min_weight <= 0:
        weights = weights - min_weight + EPSILON_WEIGHT
    return np.maximum(weights, EPSILON_WEIGHT)


def normalize_weights(weights_array: np.ndarray) -> np.ndarray:
    """Normalize weights to sum to 1.0.

    Args:
        weights_array: Array of weights.

    Returns:
        Weights normalised to sum to 1.0.

    Raises:
        DataValidationError: If weights sum to zero.
    """
    weight_sum = np.sum(weights_array)
    if np.isclose(weight_sum, 0.0):
        raise DataValidationError("Weights sum to zero; cannot normalise.")
    return weights_array / weight_sum