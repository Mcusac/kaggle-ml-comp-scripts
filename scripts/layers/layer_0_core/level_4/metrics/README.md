# level_4.metrics

## Purpose

Unified metric entry points for classification/regression and a configurable weighted R2 builder for contest-style regression scoring.

## Contents

| Module | Description |
|--------|-------------|
| `calculate_metrics.py` | Task-aware metric dispatch (`calculate_metrics`) and metric lookup by name (`calculate_metric_by_name`) |
| `weighted_r2.py` | Factory for weighted R2 calculators with optional derived-target preprocessing |
| `__init__.py` | Package exports |

## Public API

| Export | Description |
|--------|-------------|
| `calculate_metrics` | Calculate metrics by `task_type`, with optional contest metric routing |
| `calculate_metric_by_name` | Calculate a registered metric directly by metric name |
| `create_weighted_r2_calculator` | Build `(y_pred, y_true, config?) -> (weighted_r2, r2_per_target)` calculator |

## Dependencies

- `calculate_metrics.py`
  - **level_0**: `get_logger`
  - **level_1**: `get_metric`, `list_metrics`
  - **level_3**: `calculate_classification_metrics`, `calculate_regression_metrics`
- `weighted_r2.py`
  - **level_2**: `validate_paired_arrays`
  - **level_3**: `calculate_r2_per_target`, `prepare_weighted_arrays`, `calculate_weighted_r2_from_arrays`

## Usage Example

```python
from layers.layer_0_core.level_4 import calculate_metrics, create_weighted_r2_calculator

# Generic task-based dispatch
metrics = calculate_metrics("regression", y_true, y_pred, target_names=["x", "y"])

# Contest-style weighted R2
calc = create_weighted_r2_calculator(
    weights={"x": 0.7, "y": 0.3},
    target_order=["x", "y"],
)
weighted_r2, r2_per_target = calc(y_pred, y_true)
```
