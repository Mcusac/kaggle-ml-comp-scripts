"""Evaluation package for metrics and losses."""

from .loss_types import (
    LossType,
    BaseLoss,
    FocalLoss,
    WeightedBCELoss,
    SparseBCEWithLogitsLoss,
    LabelSmoothingBCEWithLogitsLoss,
)
from .metric_registry import (
    MetricRegistry,
    register_metric,
    get_metric,
    list_metrics,
)
from .results_analysis import (
    calculate_fold_statistics,
    generate_cv_test_gap_warnings,
)

__all__ = [
    "LossType",
    "BaseLoss",
    "FocalLoss",
    "WeightedBCELoss",
    "SparseBCEWithLogitsLoss",
    "LabelSmoothingBCEWithLogitsLoss",
    "MetricRegistry",
    "register_metric",
    "get_metric",
    "list_metrics",
    "calculate_fold_statistics",
    "generate_cv_test_gap_warnings",
]
