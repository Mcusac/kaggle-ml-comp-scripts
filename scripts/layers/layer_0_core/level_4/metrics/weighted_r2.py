"""Configurable weighted R² metric for regression contests."""

import numpy as np

from typing import Any, Callable, Dict, List, Optional, Tuple

from layers.layer_0_core.level_2 import validate_paired_arrays
from layers.layer_0_core.level_3 import (
    calculate_r2_per_target,
    calculate_weighted_r2_from_arrays,
    prepare_weighted_arrays,
)


def create_weighted_r2_calculator(
    weights: Dict[str, float],
    target_order: List[str],
    derived_target_fn: Optional[Callable[[np.ndarray], np.ndarray]] = None,
) -> Callable[[np.ndarray, np.ndarray, Optional[Any]], Tuple[float, np.ndarray]]:
    """
    Create a weighted R² calculator function.

    Args:
        weights: Target name -> weight mapping.
        target_order: Ordered list of target names.
        derived_target_fn: Optional function to compute derived targets from primary.
                          If None, y_pred and y_true are used as-is.

    Returns:
        Function (y_pred, y_true, config?) -> (weighted_r2, r2_per_target).
    """
    def calc(
        y_pred: np.ndarray,
        y_true: np.ndarray,
        config: Optional[Any] = None,
    ) -> Tuple[float, np.ndarray]:
        if derived_target_fn is not None:
            y_pred = derived_target_fn(y_pred)
            y_true = derived_target_fn(y_true)
        validate_paired_arrays(y_true, y_pred)
        if y_true.shape[1] != len(target_order):
            raise ValueError(
                f"Expected {len(target_order)} targets, got {y_true.shape[1]}"
            )
        y_true_flat, y_pred_flat, weights_flat = prepare_weighted_arrays(
            y_true, y_pred, weights, target_order
        )
        weighted_r2 = calculate_weighted_r2_from_arrays(
            y_true_flat, y_pred_flat, weights_flat
        )
        r2_per_target = calculate_r2_per_target(y_true, y_pred)
        return weighted_r2, r2_per_target

    return calc
