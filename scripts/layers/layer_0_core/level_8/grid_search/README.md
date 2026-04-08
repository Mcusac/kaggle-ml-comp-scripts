# level_8.grid_search

## Purpose

Dataset grid search over preprocessing/augmentation variants, plus end-to-end variant config extraction and result dict construction for hyperparameter grid search workflows.

## Contents

| Module | Description |
|--------|-------------|
| `dataset_grid_search.py` | `DatasetGridSearch` extending `GridSearchBase` |
| `end_to_end_variants.py` | `extract_variant_config`, `create_end_to_end_variant_result` |

## Public API

| Name | Description |
|------|-------------|
| `DatasetGridSearch` | Grid search over dataset preprocessing/augmentation variants |
| `extract_variant_config` | Extract config from variant for end-to-end grid search |
| `create_end_to_end_variant_result` | Build result dict for end-to-end variant |

## Dependencies

- **level_0**: Grid search type constants, config validation errors (via `extract_variant_config`)
- **level_1**: `generate_variant_grid`
- **level_6**: `GridSearchBase`, variant key helpers, `get_default_hyperparameters`
- **level_7**: `run_single_variant`, `build_success_result`, `build_error_result`

## Usage Example

```python
from level_8 import DatasetGridSearch, extract_variant_config, create_end_to_end_variant_result

grid_search = DatasetGridSearch(config=config, train_pipeline_fn=my_train_fn)
# results = grid_search.run()  # per GridSearchBase API

variant_config, model, n_folds, batch_size, variant_id, data_root = extract_variant_config(
    variant_config=config, param_names=["lr", "bs"], variant=(1e-3, 32), variant_index=0
)

result = create_end_to_end_variant_result(
    variant_index=0,
    variant_id="variant_0000",
    cv_score=0.85,
    fold_scores=[0.84, 0.86],
    hyperparameters={},
    config=config,
    batch_size_used=32,
)
```
