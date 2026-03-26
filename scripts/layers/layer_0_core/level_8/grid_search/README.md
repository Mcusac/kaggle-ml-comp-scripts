# level_8.grid_search

## Purpose

Dataset grid search and end-to-end variant helpers: grid search over preprocessing/augmentation variants, and config extraction plus result building for end-to-end (vision/tabular) grid search workflows.

## Contents

| Module | Description |
|--------|-------------|
| `dataset_grid_search.py` | Dataset grid search over preprocessing and augmentation variants |
| `end_to_end_variant_helpers.py` | Config extraction and result builders for end-to-end variants |

## Public API

| Name | Description |
|------|-------------|
| `DatasetGridSearch` | Grid search over dataset preprocessing/augmentation variants |
| `extract_variant_config` | Extract config from variant for end-to-end grid search |
| `create_end_to_end_variant_result` | Build result dict for end-to-end variant |

## Dependencies

- **level_0**: get_logger, GRID_SEARCH_TYPE_DATASET, RESULTS_FILE_GRIDSEARCH, ConfigValidationError
- **level_1**: generate_variant_grid
- **level_6**: GridSearchBase, create_variant_key, create_variant_key_from_result, get_default_hyperparameters
- **level_7**: run_single_variant, build_success_result, build_error_result

## Usage Example

```python
from level_8 import DatasetGridSearch, extract_variant_config, create_end_to_end_variant_result

# Dataset grid search (requires train_pipeline_fn from contest layer)
grid_search = DatasetGridSearch(config=config, train_pipeline_fn=my_train_fn)
results = grid_search.run()

# Extract variant config for end-to-end grid search
variant_config, model, n_folds, batch_size, variant_id, data_root = extract_variant_config(
    variant_config=config, param_names=["lr", "bs"], variant=(1e-3, 32), variant_index=0
)

# Build result dict
result = create_end_to_end_variant_result(
    variant_index=0, variant_id="variant_0000", cv_score=0.85, fold_scores=[0.84, 0.86],
    hyperparameters={}, config=config, batch_size_used=32,
)
```
