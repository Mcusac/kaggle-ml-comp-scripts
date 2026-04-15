# Level 10: Hyperparameter grid search orchestration

## Purpose

Owns end-to-end hyperparameter grid search: for each variant it runs the full training pipeline supplied by the contest layer via `train_pipeline_fn`, without importing contest code.

## Contents

| Sub-package | Description |
|-------------|-------------|
| `end_to_end_grid_search` | `EndToEndGridSearch` class and `hyperparameter_grid_search_pipeline` entry point |

## Public API

| Name | Description |
|------|-------------|
| `EndToEndGridSearch` | Grid search that runs full training pipeline per hyperparameter variant |
| `hyperparameter_grid_search_pipeline` | Entry point: runs hyperparameter grid search given contest context and train pipeline |

## Dependencies

| Level | Purpose |
|-------|---------|
| level_0 | `get_logger`, `BEST_HYPERPARAMETERS_FILE`, `RESULTS_FILE_GRIDSEARCH`, `SEARCH_TYPE_THOROUGH`, `ConfigValidationError` |
| level_1 | `get_transformer_hyperparameter_grid` for parameter grid by search type |
| level_4 | `save_json` for best hyperparameters summary |
| level_7 | `HyperparameterGridSearchBase` base class |
| level_8 | `extract_variant_config`, `create_end_to_end_variant_result` |
| level_9 | `attach_paths_to_config` to wire contest paths into config |

## Contest-layer contract

- **contest_context**: Must provide `get_paths()` and `get_config()`.
- **train_pipeline_fn**: Callable `(data_root, model, n_folds, **config_overrides) -> (cv_score, fold_scores)`. Injected by contest layer; level_10 does not import contest.

## Usage Example

```python
from layers.layer_0_core.level_10 import hyperparameter_grid_search_pipeline

# Contest layer provides context and train pipeline
hyperparameter_grid_search_pipeline(
    contest_context=my_contest_context,
    train_pipeline_fn=my_train_pipeline,
    search_type="quick",
)
```
