# ensemble_strategies

Prediction combination strategies and pipeline result handlers for ensemble workflows.

## Purpose

Implements multiple strategies for combining predictions from multiple models: averaging variants, weight matrix construction, and handlers that log and validate pipeline execution results for regression, stacking, and hybrid stacking workflows.

## Contents

- `averaging.py` — `simple_average`, `weighted_average`, `value_rank_average`, `value_percentile_average`, `power_average`, `geometric_mean`, `max_ensemble`, `model_rank_weights`, `merge_submissions`
- `result_handler_common.py` — internal: `_log_pipeline_completion` shared by result handlers
- `handle_regression_ensemble_result.py` — `handle_regression_ensemble_result`: result handler for regression ensemble pipelines
- `handle_stacking_results.py` — `handle_stacking_result`, `handle_hybrid_stacking_result`: result handlers for stacking pipelines
- `pipeline_result_handler.py` — `handle_ensemble_result`: general ensemble pipeline result handler
- `weight_matrix_builder.py` — `build_weight_matrix`: build normalized per-target weight matrices

## Public API

- `model_rank_weights(scores)` — Compute model weights from rank ordering of scores
- `simple_average(predictions)` — Unweighted mean across models
- `weighted_average(predictions, weights)` — Weighted mean; weights are normalized internally
- `value_rank_average(predictions)` — Rank-based averaging
- `value_percentile_average(predictions)` — Percentile-based averaging
- `power_average(predictions, power)` — Power-weighted average
- `geometric_mean(predictions)` — Geometric mean across models
- `max_ensemble(predictions)` — Element-wise maximum across models
- `merge_submissions(dfs, weights)` — Merge submission DataFrames by weighted averaging
- `handle_regression_ensemble_result(returncode, stdout_lines, log_file, config)` — Log and validate a regression ensemble pipeline result
- `handle_stacking_result(returncode, stdout_lines, log_file, stacking_config)` — Log and validate a stacking pipeline result
- `handle_hybrid_stacking_result(returncode, stdout_lines, log_file, config)` — Log and validate a hybrid stacking pipeline result
- `handle_ensemble_result(returncode, stdout_lines, log_file, config)` — Log and validate a general ensemble pipeline result
- `build_weight_matrix(per_target_weights, target_names, num_models)` — Build normalized (targets × models) weight matrix

## Dependencies

- **level_0** — `ExecutionResult`, `get_logger`, `is_kaggle`, `DataValidationError`
- **level_1** — `validate_execution_result`, `resolve_environment_path`, `validate_predictions_for_ensemble`, `normalize_weights`, `ensure_positive_weights`

## Usage Example

```python
import numpy as np
from level_2.ensemble_strategies import weighted_average, build_weight_matrix

predictions = np.stack([model1_preds, model2_preds, model3_preds], axis=0)
weights = np.array([0.5, 0.3, 0.2])
ensemble_preds = weighted_average(predictions, weights)
```
