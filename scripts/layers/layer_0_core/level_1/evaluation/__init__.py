"""Auto-generated package exports."""


from .loss_types import (
    BaseLoss,
    F,
    FocalLoss,
    LabelSmoothingBCEWithLogitsLoss,
    LossType,
    SparseBCEWithLogitsLoss,
    WeightedBCELoss,
)

from .metric_registry import (
    MetricRegistry,
    get_metric,
    list_metrics,
    register_metric,
)

from .results_analysis import (
    calculate_fold_statistics,
    generate_cv_test_gap_warnings,
)

__all__ = [
    "BaseLoss",
    "F",
    "FocalLoss",
    "LabelSmoothingBCEWithLogitsLoss",
    "LossType",
    "MetricRegistry",
    "SparseBCEWithLogitsLoss",
    "WeightedBCELoss",
    "calculate_fold_statistics",
    "generate_cv_test_gap_warnings",
    "get_metric",
    "list_metrics",
    "register_metric",
]
