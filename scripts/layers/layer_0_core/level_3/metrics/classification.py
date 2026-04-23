"""Generic classification metrics.

sklearn.metrics is a hard dependency at this level: the metric functions
delegate directly to sklearn implementations rather than using the lazy-loader
pattern, because sklearn is required for the metric classes to function at all
and a controlled warning on unavailability adds no value here.
"""

import numpy as np

from typing import Dict, Optional
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    accuracy_score,
)

from layers.layer_0_core.level_0 import Metric, get_logger
from layers.layer_0_core.level_1 import register_metric
from layers.layer_0_core.level_2 import validate_paired_arrays

_logger = get_logger(__name__)


# =====================================================
# Individual Metric Calculations
# =====================================================

def calculate_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    sample_weight: Optional[np.ndarray] = None,
) -> float:
    """
    Calculate accuracy score.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        sample_weight: Optional sample weights.

    Returns:
        Accuracy value in range [0, 1].
    """
    validate_paired_arrays(y_true, y_pred)
    return float(accuracy_score(y_true, y_pred, sample_weight=sample_weight))


def calculate_f1(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    average: str = "macro",
) -> float:
    """
    Calculate F1 score.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        average: Averaging strategy ('macro', 'micro', 'weighted', 'binary').

    Returns:
        F1 score value.
    """
    validate_paired_arrays(y_true, y_pred)
    return float(f1_score(y_true, y_pred, average=average, zero_division=0))


def calculate_precision(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    average: str = "macro",
) -> float:
    """
    Calculate precision score.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        average: Averaging strategy ('macro', 'micro', 'weighted', 'binary').

    Returns:
        Precision score value.
    """
    validate_paired_arrays(y_true, y_pred)
    return float(precision_score(y_true, y_pred, average=average, zero_division=0))


def calculate_recall(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    average: str = "macro",
) -> float:
    """
    Calculate recall score.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        average: Averaging strategy ('macro', 'micro', 'weighted', 'binary').

    Returns:
        Recall score value.
    """
    validate_paired_arrays(y_true, y_pred)
    return float(recall_score(y_true, y_pred, average=average, zero_division=0))


def calculate_roc_auc(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    average: str = "macro",
    multi_class: str = "ovr",
) -> float:
    """
    Calculate ROC-AUC score.

    Args:
        y_true: Ground truth labels.
        y_pred_proba: Predicted probabilities.
        average: Averaging strategy ('macro', 'micro', 'weighted').
        multi_class: Strategy for multi-class ('ovr', 'ovo').

    Returns:
        ROC-AUC score value, or 0.0 if calculation fails.
    """
    validate_paired_arrays(y_true, y_pred_proba, allow_different_shapes=True)

    try:
        return float(
            roc_auc_score(
                y_true,
                y_pred_proba,
                average=average,
                multi_class=multi_class,
            )
        )
    except ValueError as e:
        _logger.warning(f"ROC-AUC calculation failed: {e}. Returning 0.0")
        return 0.0


# =====================================================
# Metric Classes
# =====================================================

class AccuracyMetric(Metric):
    """Accuracy metric class."""

    def __init__(self):
        super().__init__("accuracy")

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sample_weight: Optional[np.ndarray] = None,
        **kwargs,
    ) -> float:
        return calculate_accuracy(y_true, y_pred, sample_weight)


class F1Metric(Metric):
    """F1 score metric class."""

    def __init__(self, average: str = "macro"):
        super().__init__(f"f1_{average}")
        self.average = average

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs,
    ) -> float:
        average = kwargs.get("average", self.average)
        return calculate_f1(y_true, y_pred, average)


class PrecisionMetric(Metric):
    """Precision metric class."""

    def __init__(self, average: str = "macro"):
        super().__init__(f"precision_{average}")
        self.average = average

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs,
    ) -> float:
        average = kwargs.get("average", self.average)
        return calculate_precision(y_true, y_pred, average)


class RecallMetric(Metric):
    """Recall metric class."""

    def __init__(self, average: str = "macro"):
        super().__init__(f"recall_{average}")
        self.average = average

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs,
    ) -> float:
        average = kwargs.get("average", self.average)
        return calculate_recall(y_true, y_pred, average)


class ROCAUCMetric(Metric):
    """ROC-AUC metric class."""

    def __init__(self, average: str = "macro"):
        super().__init__(f"roc_auc_{average}")
        self.average = average

    def calculate(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        **kwargs,
    ) -> float:
        average = kwargs.get("average", self.average)
        multi_class = kwargs.get("multi_class", "ovr")
        return calculate_roc_auc(y_true, y_pred_proba, average, multi_class)


# =====================================================
# Combined Metrics Calculator
# =====================================================

def calculate_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_pred_proba: Optional[np.ndarray] = None,
    average: str = "macro",
    sample_weight: Optional[np.ndarray] = None,
) -> Dict[str, float]:
    """
    Calculate comprehensive classification metrics.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        y_pred_proba: Optional predicted probabilities for ROC-AUC.
        average: Averaging strategy for multi-class metrics.
        sample_weight: Optional sample weights.

    Returns:
        Dictionary of metric name -> value.
    """
    validate_paired_arrays(y_true, y_pred)

    metrics = {
        "accuracy": calculate_accuracy(y_true, y_pred, sample_weight),
        "f1": calculate_f1(y_true, y_pred, average),
        "precision": calculate_precision(y_true, y_pred, average),
        "recall": calculate_recall(y_true, y_pred, average),
    }

    if y_pred_proba is not None:
        metrics["roc_auc"] = calculate_roc_auc(y_true, y_pred_proba, average)

    return metrics


# =====================================================
# Metric registration (private — called by metrics/__init__.py)
# =====================================================

def _register_classification_metrics() -> None:
    """Register all standard classification metrics into the global registry."""
    register_metric(AccuracyMetric())
    register_metric(F1Metric("macro"))
    register_metric(F1Metric("micro"))
    register_metric(F1Metric("weighted"))
    register_metric(PrecisionMetric("macro"))
    register_metric(RecallMetric("macro"))
    register_metric(ROCAUCMetric("macro"))