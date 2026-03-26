# end_to_end_grid_search

## Purpose

End-to-end hyperparameter grid search that runs full training for each variant. Requires `contest_context` and `train_pipeline_fn` from the contest layer.

## Contents

| Item | Description |
|------|-------------|
| `pipeline.py` | `EndToEndGridSearch` and `hyperparameter_grid_search_pipeline` implementation |
| `__init__.py` | Re-exports public API only (no logic) |

## Public API

| Name | Description |
|------|-------------|
| `EndToEndGridSearch` | Grid search that runs full training pipeline per hyperparameter variant |
| `hyperparameter_grid_search_pipeline` | Entry point: runs hyperparameter grid search given contest context and train pipeline |

## Dependencies

| Level | Purpose |
|-------|---------|
| level_0 | `get_logger`, `BEST_HYPERPARAMETERS_FILE`, `RESULTS_FILE_GRIDSEARCH`, `SEARCH_TYPE_THOROUGH`, `ConfigValidationError` |
| level_1 | `get_transformer_hyperparameter_grid` |
| level_4 | `save_json` |
| level_7 | `HyperparameterGridSearchBase` |
| level_8 | `extract_variant_config`, `create_end_to_end_variant_result` |
| level_9 | `attach_paths_to_config` |

## Usage Example

```python
from level_10 import hyperparameter_grid_search_pipeline

hyperparameter_grid_search_pipeline(
    contest_context=my_contest_context,
    train_pipeline_fn=my_train_pipeline,
    search_type="quick",
)
```
