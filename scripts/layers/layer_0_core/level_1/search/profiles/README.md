# search.profiles

## Purpose

Domain-specific hyperparameter grid profiles for regression, general training, and vision models.
Each profile provides default parameters and searchable variations keyed by search intensity.

## Contents

- `regression.py` — Grid profiles for LightGBM, XGBoost, and Ridge regression models.
- `training.py` — Grid profiles for general neural network training hyperparameters.
- `vision.py` — Grid profiles for vision model training hyperparameters.

## Public API

- `get_regression_grid(model_type, search_type)` — Returns a hyperparameter grid dict for the given
  regression model. `model_type`: `'lgbm'`, `'xgboost'` (alias `'xgb'`), `'ridge'`.
  `search_type`: `'defaults'`, `'quick'`, `'in_depth'`.
- `get_training_grid(search_type)` — Returns a training hyperparameter grid.
  `search_type`: `'defaults'`, `'quick'`, `'in_depth'`, `'thorough'`.
- `get_vision_grid(search_type)` — Returns a vision hyperparameter grid.
  `search_type`: `'defaults'`, `'quick'`, `'in_depth'`, `'thorough'`.

## Dependencies

- `level_0.grid_search` — `build_parameter_grid` merges defaults with varied parameters into a
  grid dict. `resolve_varied_params` selects the right varied-values dict for a given `search_type`.

## Usage Example
```python
from search.profiles import get_regression_grid, get_training_grid, get_vision_grid

regression_grid = get_regression_grid("lgbm", search_type="quick")
training_grid = get_training_grid(search_type="in_depth")
vision_grid = get_vision_grid(search_type="thorough")
```