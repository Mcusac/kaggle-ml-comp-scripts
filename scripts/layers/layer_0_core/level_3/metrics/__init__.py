"""Metrics: classification and regression implementations.

Importing this package auto-registers all standard metrics into the global
metric registry (level_1.register_metric). This is intentional: any module
that imports level_3.metrics gets a fully populated registry as a side effect,
so callers never have to call register_*() themselves. The registration
functions are private (_register_*) because they are an implementation detail
of this package's import contract, not part of its public API.
"""

from .classification import (
    calculate_accuracy,
    calculate_f1,
    calculate_precision,
    calculate_recall,
    calculate_roc_auc,
    AccuracyMetric,
    F1Metric,
    PrecisionMetric,
    RecallMetric,
    ROCAUCMetric,
    calculate_classification_metrics,
    _register_classification_metrics,
)

from .regression import (
    calculate_rmse,
    calculate_mae,
    calculate_r2,
    calculate_r2_per_target,
    calculate_weighted_r2_from_arrays,
    prepare_weighted_arrays,
    calculate_weighted_rmse,
    RMSEMetric,
    MAEMetric,
    R2Metric,
    WeightedRMSEMetric,
    calculate_regression_metrics,
    _register_regression_metrics,
)

# Auto-register all standard metrics when this package is imported.
_register_classification_metrics()
_register_regression_metrics()

__all__ = [
    # Classification — functions
    "calculate_accuracy",
    "calculate_f1",
    "calculate_precision",
    "calculate_recall",
    "calculate_roc_auc",
    "calculate_classification_metrics",
    # Classification — classes
    "AccuracyMetric",
    "F1Metric",
    "PrecisionMetric",
    "RecallMetric",
    "ROCAUCMetric",
    # Regression — functions
    "calculate_rmse",
    "calculate_mae",
    "calculate_r2",
    "calculate_r2_per_target",
    "calculate_weighted_r2_from_arrays",
    "prepare_weighted_arrays",
    "calculate_weighted_rmse",
    "calculate_regression_metrics",
    # Regression — classes
    "RMSEMetric",
    "MAEMetric",
    "R2Metric",
    "WeightedRMSEMetric",
]