"""Validation guards for ensemble prediction sets."""

import numpy as np

from typing import List, Optional, Tuple

from layers.layer_0_core.level_0 import validate_predictions_list, validate_same_shape


def validate_predictions_for_ensemble(
    predictions_list: List[np.ndarray],
    require_weights: bool = False,
    weights: Optional[List[float]] = None,
) -> Tuple[Tuple[int, ...], np.ndarray]:
    """
    Validate a list of predictions for ensemble use, optionally with weights.

    Args:
        predictions_list: List of prediction arrays (one per model).
        require_weights:  If True, weights must be provided and length-matched.
        weights:          Optional list of per-model weights.

    Returns:
        Tuple of (common shape, stacked predictions array).

    Raises:
        ValueError: If validation fails or weights are required but absent/mismatched.
    """
    validate_predictions_list(predictions_list)

    if require_weights:
        if weights is None:
            raise ValueError("weights are required for this ensemble method")
        if len(weights) != len(predictions_list):
            raise ValueError(
                f"Number of weights ({len(weights)}) must match "
                f"number of predictions ({len(predictions_list)})"
            )

    shape = validate_same_shape(predictions_list)
    stacked = np.stack(predictions_list, axis=0)
    return shape, stacked


def validate_paired_predictions(
    train_predictions: List[np.ndarray],
    val_predictions: List[np.ndarray],
) -> int:
    """
    Validate that train and validation prediction lists are compatible.

    Checks that both lists are non-empty, have the same number of models,
    and that the target dimensions match.

    Args:
        train_predictions: Per-model training predictions.
        val_predictions:   Per-model validation predictions.

    Returns:
        Number of models (length of either list).

    Raises:
        ValueError: If lists are empty, unequal in length, or target dims differ.
    """
    validate_predictions_list(train_predictions, "train_predictions")
    validate_predictions_list(val_predictions, "val_predictions")

    if len(train_predictions) != len(val_predictions):
        raise ValueError("Number of train and validation models must match")

    train_shape = train_predictions[0].shape
    val_shape = val_predictions[0].shape
    if train_shape[1:] != val_shape[1:]:
        raise ValueError(
            f"Train and val predictions must match on target dimensions. "
            f"Train: {train_shape}, Val: {val_shape}"
        )

    return len(train_predictions)