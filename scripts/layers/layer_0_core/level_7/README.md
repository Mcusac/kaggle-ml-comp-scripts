# level_7

## Purpose

Level 7 provides grid search results detection, variant result builders, hyperparameter grid search base, dataset variant execution, and factory functions for tabular models and ensembling methods.

## Contents

| Sub-package / Module | Description |
|----------------------|-------------|
| `grid_search/` | Grid search results detection, hyperparameter base, variant builders, dataset executor |
| `factories/` | Tabular model and ensembling method creation by name |

## Public API

| Name | Description |
|------|-------------|
| `calculate_focused_grid_size` | Calculate focused grid size before running search |
| `auto_detect_grid_search_results` | Auto-detect grid search results files |
| `get_completed_count` | Count completed variants from results file |
| `build_success_result` | Build success variant result dict |
| `build_error_result` | Build error variant result dict |
| `create_ensembling_method` | Factory: create ensembling method by name |
| `HyperparameterGridSearchBase` | Base class for hyperparameter grid searches |
| `run_single_variant` | Run training for a single dataset variant |
| `run_variant_cleanup` | Per-variant checkpoint cleanup after a variant |
| `run_final_cleanup` | Final cleanup after grid search |
| `create_tabular_model` | Factory: create tabular model by type |

## Dependencies

- **level_0**: Logging, validation errors, dataset grid-search model-dir constant, shared result-dict helpers, `EnsemblingMethod` abstraction
- **level_1**: `cleanup_gpu_memory` for dataset variant runs
- **level_3**: `PerTargetWeightedEnsemble` for the ensembling factory
- **level_5**: `BaseTabularModel` type for tabular model factory
- **level_6**: Concrete tabular and ensembling classes, `GridSearchBase`, grid-search results/cleanup utilities, `create_variant_specific_data`

## Usage Example

```python
from level_7 import (
    create_tabular_model,
    create_ensembling_method,
    HyperparameterGridSearchBase,
    run_single_variant,
    build_success_result,
    auto_detect_grid_search_results,
)

# Create tabular model by type
model = create_tabular_model("ridge", input_dim=100, output_dim=1)

# Create ensembling method
ensemble = create_ensembling_method("weighted_average")

# Auto-detect grid search results
results_file = auto_detect_grid_search_results(model_name="my_model")
```
