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
| `build_success_result` | Build success variant result dict |
| `build_error_result` | Build error variant result dict |
| `create_ensembling_method` | Factory: create ensembling method by name |
| `HyperparameterGridSearchBase` | Base class for hyperparameter grid searches |
| `run_single_variant` | Run training for a single dataset variant |
| `create_tabular_model` | Factory: create tabular model by type |

## Dependencies

- **level_0**: Logging, config, paths, grid search constants, result builders
- **level_1**: GPU cleanup, transformer hyperparameter grid, environment paths
- **level_3**: PerTargetWeightedEnsemble
- **level_5**: BaseTabularModel
- **level_5**: get_focused_parameter_grid and grid-search persistence/analysis helpers
- **level_6**: GridSearchBase, tabular models, ensembling methods, variant helpers (also re-exports focused-grid helpers from level_5)

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
