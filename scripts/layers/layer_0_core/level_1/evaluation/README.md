# evaluation

## Purpose
Custom loss functions, a metric registry, and CV fold score analysis utilities.

## Contents
- `loss_types.py` — `BaseLoss`, `FocalLoss`, `WeightedBCELoss`, `SparseBCEWithLogitsLoss`, `LabelSmoothingBCEWithLogitsLoss`, `LossType`
- `metric_registry.py` — `MetricRegistry`, `register_metric`, `get_metric`, `list_metrics`
- `results_analysis.py` — `calculate_fold_statistics`, `generate_cv_test_gap_warnings`
- `weights.py` — `ensure_positive_weights`, `normalize_weights` *(currently not exported — pending decision)*

## Public API
- `LossType` — Literal type alias for supported loss names
- `BaseLoss` — Abstract base; enforces `forward(inputs, targets)` interface
- `FocalLoss(alpha, gamma, reduction)` — focal loss for class imbalance
- `WeightedBCELoss(weights, reduction)` — per-class or per-sample weighted BCE
- `SparseBCEWithLogitsLoss(pos_weight)` — memory-efficient BCE for sparse multi-label
- `LabelSmoothingBCEWithLogitsLoss(smoothing, reduction)` — label-smoothed BCE
- `MetricRegistry` — dict-backed registry for `Metric` objects
- `register_metric(metric)`, `get_metric(name)`, `list_metrics()` — global registry accessors
- `calculate_fold_statistics(fold_scores)` → dict of mean/std/min/max/range
- `generate_cv_test_gap_warnings(cv_score, fold_mean, fold_range, test_score, threshold)` → list of warning strings

## Dependencies
- `level_0` — `get_torch`, `get_logger`, `Metric`

## Usage Example
```python
from level_1.evaluation import FocalLoss, calculate_fold_statistics
loss_fn = FocalLoss(gamma=2.0)
stats = calculate_fold_statistics([0.82, 0.84, 0.81, 0.83, 0.85])
```