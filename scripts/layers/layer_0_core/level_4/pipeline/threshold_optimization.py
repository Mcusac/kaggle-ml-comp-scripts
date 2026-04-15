"""Threshold optimization for multi-label classification."""

import numpy as np

from scipy.optimize import minimize_scalar
from typing import Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_3 import (
    calculate_f1,
    calculate_precision,
    calculate_recall,
)

logger = get_logger(__name__)


def optimize_threshold(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    metric: str = 'f1',
    threshold_range: Tuple[float, float] = (0.0, 1.0)
) -> float:
    """
    Optimize prediction threshold for multi-label classification.
    
    Args:
        y_true: True binary labels (n_samples, n_labels).
        y_pred_proba: Predicted probabilities (n_samples, n_labels).
        metric: Metric to optimize ('f1', 'precision', 'recall').
        threshold_range: Range of thresholds to search.
        
    Returns:
        Optimal threshold value.
    """
    def objective(threshold):
        y_pred_binary = (y_pred_proba > threshold).astype(int)

        if metric == "f1":
            score = calculate_f1(y_true, y_pred_binary, average="macro")
        elif metric == "precision":
            score = calculate_precision(y_true, y_pred_binary, average="macro")
        elif metric == "recall":
            score = calculate_recall(y_true, y_pred_binary, average="macro")
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        return -score  # Minimize negative score (maximize score)
    
    result = minimize_scalar(
        objective,
        bounds=threshold_range,
        method='bounded'
    )
    
    optimal_threshold = result.x
    logger.info(f"Optimal threshold ({metric}): {optimal_threshold:.4f}")
    
    return optimal_threshold
