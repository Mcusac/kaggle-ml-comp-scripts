"""Prediction combination helpers."""

import numpy as np

from typing import List


def combine_predictions_loop(
    predictions_list: List[np.ndarray],
    weight_matrix: np.ndarray,
    result: np.ndarray,
) -> np.ndarray:
    """
    Reference implementation using Python loops.

    Args:
        predictions_list: List of arrays, each (samples, targets).
        weight_matrix: Array of shape (targets, models).
        result: Preallocated output array (samples, targets); modified in-place.

    Returns:
        The result array (same object as input result, modified in-place).
    """

    num_targets, num_models = weight_matrix.shape

    for target_idx in range(num_targets):
        for model_idx, pred in enumerate(predictions_list):
            result[:, target_idx] += (
                pred[:, target_idx] * weight_matrix[target_idx, model_idx]
            )

    return result


def combine_predictions_vectorized(
    predictions_list: List[np.ndarray],
    weight_matrix: np.ndarray,
) -> np.ndarray:
    """
    Vectorized implementation using NumPy tensor contraction.

    Args:
        predictions_list: List of arrays, each (samples, targets).
        weight_matrix: Array of shape (targets, models).

    Returns:
        Combined predictions array of shape (samples, targets).
    """

    pred_array = np.stack(predictions_list)  # (models, samples, targets)

    # einsum: sum_m predictions[m,s,t] * weight[t,m]
    return np.einsum("mst,tm->st", pred_array, weight_matrix)
