"""Generic regression metrics.

sklearn.metrics is a hard dependency at this level: the metric functions
delegate directly to sklearn implementations rather than using the lazy-loader
pattern, because sklearn is required for the metric classes to function at all
and a controlled warning on unavailability adds no value here.
"""

import numpy as np

from typing import Dict, List, Optional, Tuple
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score as sklearn_r2_score,
)

from level_0 import get_logger, Metric
from level_1 import register_metric
from level_2 import validate_paired_arrays

logger = get_logger(__name__)


# =====================================================
# Individual Metric Calculations
# =====================================================

def calculate_rmse(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
) -> float:
    """
    Calculate Root Mean Squared Error.

    Args:
        y_true: Ground truth values.
        y_pred: Predicted values.
        sample_weight: Optional sample weights.

    Returns:
        RMSE value.
    """
    validate_paired_arrays(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred, sample_weight=sample_weight)
    return float(np.sqrt(mse))


def calculate_mae(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
) -> float:
    """
    Calculate Mean Absolute Error.

    Args:
        y_true: Ground truth values.
        y_pred: Predicted values.
        sample_weight: Optional sample weights.

    Returns:
        MAE value.
    """
    validate_paired_arrays(y_true, y_pred)
    return float(mean_absolute_error(y_true, y_pred, sample_weight=sample_weight))


def calculate_r2(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
) -> float:
    """
    Calculate R² (coefficient of determination) score.

    Args:
        y_true: Ground truth values.
        y_pred: Predicted values.
        sample_weight: Optional sample weights.

    Returns:
        R² value. Best possible score is 1.0, can be negative.
    """
    validate_paired_arrays(y_true, y_pred)
    return float(sklearn_r2_score(y_true, y_pred, sample_weight=sample_weight))


def calculate_r2_per_target(
    y_true: np.ndarray,
    y_pred: np.ndarray,
) -> np.ndarray:
    """
    Calculate R² independently for each target column.

    Args:
        y_true: Ground truth values of shape (n_samples, n_targets).
        y_pred: Predicted values of shape (n_samples, n_targets).

    Returns:
        Float64 array of shape (n_targets,) with one R² score per target.

    Raises:
        ValueError: If inputs are not 2-D arrays.
    """
    validate_paired_arrays(y_true, y_pred)

    if y_true.ndim != 2:
        raise ValueError(f"Expected 2D arrays, got {y_true.shape}")

    return sklearn_r2_score(y_true, y_pred, multioutput="raw_values")


def prepare_weighted_arrays(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    weights: Dict[str, float],
    target_order: List[str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Prepare flattened arrays and weights for weighted R² calculation.

    Args:
        y_true: True values, shape (N, M).
        y_pred: Predicted values, shape (N, M).
        weights: Dictionary mapping target names to weights.
        target_order: Ordered list of target names.

    Returns:
        Tuple of (y_true_flat, y_pred_flat, weights_flat).
    """
    weight_array = np.array([weights[t] for t in target_order])
    y_true_flat = y_true.flatten()
    y_pred_flat = y_pred.flatten()
    n_images = y_true.shape[0]
    weights_flat = np.tile(weight_array, n_images)
    return y_true_flat, y_pred_flat, weights_flat


def calculate_weighted_r2_from_arrays(
    y_true_flat: np.ndarray,
    y_pred_flat: np.ndarray,
    weights_flat: np.ndarray,
) -> float:
    """
    Calculate weighted R² from flattened arrays.

    Formula: R² = 1 - (RSS / TSS)
    where RSS = Σ w_i * (y_true_i - y_pred_i)², TSS = Σ w_i * (y_true_i - y_mean)².
    """
    y_mean = np.average(y_true_flat, weights=weights_flat)
    rss = np.sum(weights_flat * (y_true_flat - y_pred_flat) ** 2)
    tss = np.sum(weights_flat * (y_true_flat - y_mean) ** 2)
    return float(1 - (rss / tss)) if tss > 0 else 0.0


def calculate_weighted_rmse(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_weights: Optional[np.ndarray] = None,
) -> float:
    """
    Calculate weighted RMSE across multiple targets.

    For a 1-D input, delegates to calculate_rmse (equal to unweighted RMSE).
    For a 2-D input, computes per-column RMSE and returns their weighted sum.

    Args:
        y_true: Ground truth values of shape (n_samples,) or (n_samples, n_targets).
        y_pred: Predicted values, same shape as y_true.
        target_weights: Per-target weights of shape (n_targets,). Normalised to
                        sum to 1 before use. Equal weights when None.

    Returns:
        Scalar weighted RMSE value.
    """
    validate_paired_arrays(y_true, y_pred)

    if y_true.ndim == 1:
        return calculate_rmse(y_true, y_pred)

    rmse = np.sqrt(np.mean((y_true - y_pred) ** 2, axis=0))

    if target_weights is None:
        target_weights = np.ones_like(rmse) / len(rmse)
    else:
        target_weights = np.asarray(target_weights)
        target_weights = target_weights / target_weights.sum()

    return float(np.sum(rmse * target_weights))


# =====================================================
# Metric Classes
# =====================================================

class RMSEMetric(Metric):
    """RMSE metric class."""

    def __init__(self):
        super().__init__("rmse")

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        **kwargs,
    ) -> float:
        return calculate_rmse(y_true, y_pred, sample_weight)


class MAEMetric(Metric):
    """MAE metric class."""

    def __init__(self):
        super().__init__("mae")

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        **kwargs,
    ) -> float:
        return calculate_mae(y_true, y_pred, sample_weight)


class R2Metric(Metric):
    """R² metric class."""

    def __init__(self):
        super().__init__("r2")

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        **kwargs,
    ) -> float:
        return calculate_r2(y_true, y_pred, sample_weight)


class WeightedRMSEMetric(Metric):
    """Weighted RMSE metric class."""

    def __init__(self):
        super().__init__("weighted_rmse")

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        target_weights: Optional[np.ndarray] = None,
        **kwargs,
    ) -> float:
        return calculate_weighted_rmse(y_true, y_pred, target_weights)


# =====================================================
# Combined Metrics Calculator
# =====================================================

def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_names: Optional[List[str]] = None,
    sample_weight: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """
    Calculate comprehensive regression metrics.

    Args:
        y_true: Ground truth values, shape (N,) or (N, M).
        y_pred: Predicted values, same shape as y_true.
        target_names: Optional names for each target (for multi-target output).
        sample_weight: Optional sample weights.

    Returns:
        Dictionary of metric name -> value.
        For multi-target inputs, also includes per-target rmse, mae, and r2.
    """
    validate_paired_arrays(y_true, y_pred)

    metrics = {
        "rmse": calculate_rmse(y_true, y_pred, sample_weight),
        "mae": calculate_mae(y_true, y_pred, sample_weight),
        "r2": calculate_r2(y_true, y_pred, sample_weight),
    }

    if y_true.ndim > 1 and y_true.shape[1] > 1:
        for i in range(y_true.shape[1]):
            name = target_names[i] if target_names else f"target_{i}"
            metrics[f"{name}_rmse"] = calculate_rmse(y_true[:, i], y_pred[:, i])
            metrics[f"{name}_mae"] = calculate_mae(y_true[:, i], y_pred[:, i])
            metrics[f"{name}_r2"] = calculate_r2(y_true[:, i], y_pred[:, i])

    return metrics


# =====================================================
# Metric registration (private — called by metrics/__init__.py)
# =====================================================

def _register_regression_metrics() -> None:
    """Register all standard regression metrics into the global registry."""
    register_metric(RMSEMetric())
    register_metric(MAEMetric())
    register_metric(R2Metric())
    register_metric(WeightedRMSEMetric())