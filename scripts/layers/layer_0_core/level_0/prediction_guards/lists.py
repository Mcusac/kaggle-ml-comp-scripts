"""Validation guards for lists of prediction arrays."""

from typing import List, Tuple

import numpy as np


def validate_predictions_list(
    predictions_list: List[np.ndarray],
    name: str = "predictions_list",
) -> None:
    """
    Validate that a predictions list is non-empty.

    Args:
        predictions_list: List of prediction arrays.
        name:             Name used in error messages.

    Raises:
        ValueError: If the list is empty.
    """
    if not predictions_list:
        raise ValueError(f"{name} cannot be empty")


def validate_same_shape(
    predictions_list: List[np.ndarray],
    name: str = "predictions_list",
) -> Tuple[int, ...]:
    """
    Validate that all arrays in a predictions list have identical shape.

    Args:
        predictions_list: List of prediction arrays.
        name:             Name used in error messages.

    Returns:
        The common shape shared by all arrays.

    Raises:
        ValueError: If the list is empty or shapes differ.
    """
    validate_predictions_list(predictions_list, name)
    first_shape = predictions_list[0].shape
    for idx, pred in enumerate(predictions_list[1:], 1):
        if pred.shape != first_shape:
            raise ValueError(
                f"All {name} must have identical shape. "
                f"First: {first_shape}, item {idx}: {pred.shape}"
            )
    return first_shape


def get_shape_and_targets(
    predictions_list: List[np.ndarray],
) -> Tuple[Tuple[int, ...], int]:
    """
    Extract the prediction shape and number of targets from a predictions list.

    Args:
        predictions_list: List of prediction arrays.

    Returns:
        Tuple of (shape, num_targets). num_targets is predictions.shape[1]
        for 2-D arrays, or 1 for 1-D arrays.
    """
    validate_predictions_list(predictions_list)
    shape = predictions_list[0].shape
    num_targets = shape[1] if len(shape) > 1 else 1
    return shape, num_targets