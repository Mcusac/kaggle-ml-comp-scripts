# level_7.grid_search

## Purpose

Grid search sub-package: hyperparameter base class, variant result builders, and dataset variant execution. **Results detection, focused grid sizing, and variant cleanup** are implemented in `level_6.grid_search` and imported here for the level_7 public surface.

## Contents

| Module | Description |
|--------|-------------|
| *(level_6)* `grid_search_results`, `variant_cleanup_runner` | `auto_detect_grid_search_results`, `calculate_focused_grid_size`, `run_variant_cleanup`, `run_final_cleanup`, `get_completed_count` |
| `hyperparameter_base.py` | Base class for hyperparameter grid searches |
| `variant_result_builders.py` | Build success/error variant result dicts |
| `dataset_variant_executor.py` | Run training for a single dataset variant |

## Public API

| Name | Description |
|------|-------------|
| `calculate_focused_grid_size` | Calculate focused grid size (from `level_6`) |
| `auto_detect_grid_search_results` | Auto-detect grid search results files (from `level_6`) |
| `run_variant_cleanup` | Per-variant checkpoint cleanup (from `level_6`) |
| `run_final_cleanup` | Final cleanup after grid search (from `level_6`) |
| `get_completed_count` | Count completed variants from results file (from `level_6`) |
| `build_success_result` | Build success variant result dict |
| `build_error_result` | Build error variant result dict |
| `HyperparameterGridSearchBase` | Base class for hyperparameter grid searches |
| `run_single_variant` | Run training for a single dataset variant |

## Dependencies

- **level_0**: Logging, validation, paths helpers, result-dict builders
- **level_1**: `cleanup_gpu_memory` in dataset variant execution
- **level_6**: `GridSearchBase`, `create_variant_specific_data`, results detection, cleanup orchestration (re-exported through this package)

## Usage Example

```python
from layers.layer_0_core.level_7 import (
    HyperparameterGridSearchBase,
    run_single_variant,
    build_success_result,
    auto_detect_grid_search_results,
)

# Subclass for hyperparameter grid search
class MyGridSearch(HyperparameterGridSearchBase):
    def _generate_variant_grid(self):
        return super()._generate_variant_grid()

# Auto-detect results
results_file = auto_detect_grid_search_results(model_name="my_model")
```
