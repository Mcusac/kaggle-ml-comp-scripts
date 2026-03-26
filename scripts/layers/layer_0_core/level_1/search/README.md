# search

## Purpose
Hyperparameter search infrastructure: domain-specific grid profiles and variant generation/execution primitives.

## Contents
- `search_type_utils.py` — `normalize_search_type`: validates and normalizes a search type string
- `profiles/` — Domain hyperparameter grid definitions (regression, training, vision)
- `variants/` — Variant grid generation, execution loop, score tracking, parameter grid resolution

## Public API
- `normalize_search_type(value)` → validated search type string
- From `profiles/`: `get_regression_grid`, `get_training_grid`, `get_vision_grid`
- From `variants/`: `generate_variant_grid`, `log_variant_header`, `execute_grid_search_core`, `resolve_param_grid`, `select_best_score`

## Dependencies
- `level_0` — `get_logger`, `ConfigValidationError`, `GRID_SEARCH_TYPES`, `build_parameter_grid`, `resolve_varied_params`, `generate_power_set`

## Usage Example
```python
from level_1.search import get_training_grid, generate_variant_grid
grid = get_training_grid(search_type="quick")
variants = generate_variant_grid(preprocessors, augmenters)
```