"""Validation guards for individual numpy arrays."""

import numpy as np


def validate_predictions_shape(
    predictions: np.ndarray,
    expected_count: int,
    expected_cols: int = 3,
) -> None:
    """
    Validate that a predictions array has the expected 2-D shape.

    Args:
        predictions:    Array to validate.
        expected_count: Expected number of rows (samples).
        expected_cols:  Expected number of columns (targets/outputs).

    Raises:
        TypeError:  If predictions is not a numpy array.
        ValueError: If shape does not match expectations.
    """
    if not isinstance(predictions, np.ndarray):
        raise TypeError(f"predictions must be numpy array, got {type(predictions)}")
    if predictions.ndim != 2:
        raise ValueError(f"Predictions must be 2D, got shape {predictions.shape}")
    if predictions.shape[1] != expected_cols:
        raise ValueError(
            f"Predictions must have {expected_cols} columns, got {predictions.shape[1]}"
        )
    if predictions.shape[0] != expected_count:
        raise ValueError(
            f"Predictions count ({predictions.shape[0]}) != expected ({expected_count})"
        )


def validate_targets(
    y_val: np.ndarray,
    n_samples: int,
    n_targets: int,
) -> None:
    """
    Validate a target array against expected sample and target counts.

    Args:
        y_val:      Target array to validate.
        n_samples:  Expected number of samples (rows).
        n_targets:  Expected number of targets (columns for 2-D arrays).

    Raises:
        ValueError: If shape does not match expectations.
    """
    if y_val.shape[0] != n_samples:
        raise ValueError(
            f"y_val must have {n_samples} samples, got {y_val.shape[0]}"
        )
    if y_val.ndim == 2 and y_val.shape[1] != n_targets:
        raise ValueError(
            f"y_val must have {n_targets} targets, got {y_val.shape}"
        )