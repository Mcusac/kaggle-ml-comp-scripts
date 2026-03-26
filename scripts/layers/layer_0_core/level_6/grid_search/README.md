# level_6.grid_search

## Purpose

Grid search infrastructure: base class, result handlers, and variant grid. Analysis, checkpoint cleanup, variant tracking helpers, and result persistence live in **level_5.grid_search**; this package re-exports those symbols via `from level_5 import ...` so `from level_6 import get_focused_parameter_grid` remains valid.

## Contents

- `grid_search_base.py` — GridSearchBase abstract class
- `result_handlers.py` — handle_hyperparameter_grid_search_result, handle_dataset_grid_search_result, handle_regression_grid_search_result
- `variant_grid.py` — create_variant_key, create_variant_specific_data, etc.

Focused grid, cleanup, and variant helpers are implemented under [level_5/grid_search](../../level_5/grid_search/README.md).

## Public API

| Name | Description |
|------|-------------|
| `GridSearchBase` | Abstract base for grid search pipelines |
| `handle_hyperparameter_grid_search_result` | Handle hyperparameter grid search CLI result |
| `handle_dataset_grid_search_result` | Handle dataset grid search CLI result |
| `handle_regression_grid_search_result` | Handle regression grid search CLI result |
| `get_focused_parameter_grid` | Focused grid from previous results (re-exported from level_5) |
| `create_variant_specific_data` | Create variant-specific data dict |
| `create_variant_key` | Create variant key for deduplication |
| `create_variant_key_from_result` | Create variant key from result dict |
| `create_regression_variant_key_from_result` | Create regression variant key |
| `get_default_hyperparameters` | Default transformer hyperparameters |
| `cleanup_grid_search_checkpoints_retroactive`, `cleanup_checkpoints` | Checkpoint pruning (re-exported from level_5) |
| `load_completed_variants_helper`, `get_next_variant_index`, `save_variant_result_helper` | Variant tracking (re-exported from level_5) |
| `load_raw_results`, `extract_top_results`, `extract_parameter_ranges`, `analyze_results_for_focused_grid` | Result analysis (re-exported from level_5) |

Per-variant cleanup orchestration (`variant_cleanup_runner`) lives in **level_7.grid_search**.

## Dependencies

- **level_0**: ensure_dir, get_logger (via base / handlers)
- **level_1**: BasePipeline, execute_variants, resolve_environment_path
- **level_4**: load_json
- **level_5**: grid search persistence, analysis, cleanup, variant tracking (re-exported here)

## Usage Example

```python
from level_6 import GridSearchBase, create_variant_key

variant_key = create_variant_key(
    config, preprocessing_list, augmentation_list, hyperparameters
)
```

For focused grid or retroactive cleanup, prefer importing from **level_5** when the caller already depends on level_5:

```python
from level_5 import get_focused_parameter_grid, cleanup_grid_search_checkpoints_retroactive
```
