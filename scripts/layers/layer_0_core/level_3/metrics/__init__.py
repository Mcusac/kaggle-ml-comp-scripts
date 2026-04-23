"""Auto-generated package exports."""


from .classification import (
    AccuracyMetric,
    F1Metric,
    PrecisionMetric,
    ROCAUCMetric,
    RecallMetric,
    calculate_accuracy,
    calculate_classification_metrics,
    calculate_f1,
    calculate_precision,
    calculate_recall,
    calculate_roc_auc,
)

from .regression import (
    MAEMetric,
    R2Metric,
    RMSEMetric,
    WeightedRMSEMetric,
    calculate_mae,
    calculate_r2,
    calculate_r2_per_target,
    calculate_regression_metrics,
    calculate_rmse,
    calculate_weighted_r2_from_arrays,
    calculate_weighted_rmse,
    prepare_weighted_arrays,
)

__all__ = [
    "AccuracyMetric",
    "F1Metric",
    "MAEMetric",
    "PrecisionMetric",
    "R2Metric",
    "RMSEMetric",
    "ROCAUCMetric",
    "RecallMetric",
    "WeightedRMSEMetric",
    "calculate_accuracy",
    "calculate_classification_metrics",
    "calculate_f1",
    "calculate_mae",
    "calculate_precision",
    "calculate_r2",
    "calculate_r2_per_target",
    "calculate_recall",
    "calculate_regression_metrics",
    "calculate_rmse",
    "calculate_roc_auc",
    "calculate_weighted_r2_from_arrays",
    "calculate_weighted_rmse",
    "prepare_weighted_arrays",
]
