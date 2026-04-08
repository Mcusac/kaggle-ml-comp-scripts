# ensemble_strategies

Prediction combination strategies and shared pipeline completion logging for ensemble workflows.

## Purpose

Combines predictions from multiple models via averaging and related statistics, builds per-target weight matrices, and exposes a single logging helper used by higher-level pipeline result handlers.

## Contents

- `averaging.py` — `simple_average`, `weighted_average`, `value_rank_average`, `value_percentile_average`, `power_average`, `geometric_mean`, `max_ensemble`, `model_rank_weights`, `merge_submissions`
- `result_handler_common.py` — `log_pipeline_completion` for structured success/error logging after external pipeline runs
- `weight_matrix_builder.py` — `build_weight_matrix` for normalized per-target model weights

Higher-level handlers (e.g. stacking, regression ensemble) live under `level_3` and import `log_pipeline_completion` from this package.

## Public API

Exports are defined in `__init__.py` / `__all__`. Notable symbols:

- Averaging: `model_rank_weights`, `simple_average`, `weighted_average`, `value_rank_average`, `value_percentile_average`, `power_average`, `geometric_mean`, `max_ensemble`, `merge_submissions`
- `log_pipeline_completion` — validate non-zero exit codes and log summary lines for a completed pipeline operation
- `build_weight_matrix` — build a `(targets × models)` weight matrix from named per-target weight lists

## Dependencies

- **level_0** — `ExecutionResult`, `get_logger`, `DataValidationError`
- **level_1** — `validate_execution_result`, `validate_predictions_for_ensemble`, `normalize_weights`, `ensure_positive_weights`

## Usage Example

```python
import numpy as np
from level_2 import weighted_average, build_weight_matrix

predictions = np.stack([model1_preds, model2_preds, model3_preds], axis=0)
weights = np.array([0.5, 0.3, 0.2])
ensemble_preds = weighted_average(predictions, weights.tolist())
```
