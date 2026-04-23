# level_7.grid_search

## Purpose

Grid search sub-package: hyperparameter base class, variant result builders, and dataset variant execution. **Results detection, focused grid sizing, and variant cleanup** are implemented in `level_6.grid_search` and should be imported from `level_6` directly.

## Contents

| Module | Description |
|--------|-------------|
| `hyperparameter_base.py` | Base class for hyperparameter grid searches |
| `variant_result_builders.py` | Build success/error variant result dicts |
| `dataset_variant_executor.py` | Run training for a single dataset variant |

## Public API

| Name | Description |
|------|-------------|
| `build_success_result` | Build success variant result dict |
| `build_error_result` | Build error variant result dict |
| `HyperparameterGridSearchBase` | Base class for hyperparameter grid searches |
| `run_single_variant` | Run training for a single dataset variant |

## Dependencies

- **level_0**: Logging, validation, paths helpers, result-dict builders
- **level_1**: `cleanup_gpu_memory` in dataset variant execution
- **level_6**: `GridSearchBase`, `create_variant_specific_data`, results detection, cleanup orchestration

## Usage Example

```python
from layers.layer_0_core.level_7 import (
    HyperparameterGridSearchBase,
    run_single_variant,
    build_success_result,
)
from layers.layer_0_core.level_6.grid_search import auto_detect_grid_search_results

# Subclass for hyperparameter grid search
class MyGridSearch(HyperparameterGridSearchBase):
    def _generate_variant_grid(self):
        return super()._generate_variant_grid()

# Auto-detect results
results_file = auto_detect_grid_search_results(model_name="my_model")
```
