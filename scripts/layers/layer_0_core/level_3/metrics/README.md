# level_3 metrics

Classification and regression metric implementations. Importing this package auto-registers all standard metrics into the global registry via `level_1.register_metric`.

## Purpose

Provides concrete metric functions and `Metric` subclasses for classification and regression tasks. Auto-registers all standard metrics on import so callers never invoke `register_*` directly.

## Contents

- `classification.py` — Accuracy, F1, Precision, Recall, ROC-AUC functions and metric classes; `_register_classification_metrics` (private, called at import).
- `regression.py` — RMSE, MAE, R², R² per target, Weighted RMSE functions and metric classes; `_register_regression_metrics` (private, called at import).

## Public API

- `calculate_accuracy`, `calculate_f1`, `calculate_precision`, `calculate_recall`, `calculate_roc_auc` — individual classification metric functions.
- `calculate_classification_metrics` — compute all classification metrics in one call.
- `AccuracyMetric`, `F1Metric`, `PrecisionMetric`, `RecallMetric`, `ROCAUCMetric` — `Metric` subclasses for registry use.
- `calculate_rmse`, `calculate_mae`, `calculate_r2`, `calculate_r2_per_target`, `calculate_weighted_rmse` — individual regression metric functions.
- `calculate_regression_metrics` — compute all regression metrics in one call.
- `RMSEMetric`, `MAEMetric`, `R2Metric`, `WeightedRMSEMetric` — `Metric` subclasses for registry use.

## Dependencies

- **level_0** — `Metric` (base class), `get_logger`, error types.
- **level_1** — `register_metric` (populates the global metric registry on import).
- **level_2** — `validate_paired_arrays` (input validation for all metric functions).

## Usage Example

```python
from layers.layer_0_core.level_3.metrics import calculate_accuracy, calculate_rmse, RMSEMetric

acc = calculate_accuracy(y_true, y_pred)
rmse = calculate_rmse(y_true, y_pred)
metric = RMSEMetric()
score = metric.calculate(y_true, y_pred)
```
