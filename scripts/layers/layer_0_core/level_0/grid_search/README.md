# Grid Search

Parameter space, combinatorics, result builders, and result selection for hyperparameter tuning.

## Purpose

Constants for grid search types and search modes. Build parameter grids, calculate combinations, generate power sets, assemble variant result dicts, and select best variants from experiment results.

## Contents

- `constants.py` – Grid search type identifiers, search types, file names
- `param_space.py` – `calculate_total_combinations`, `generate_param_combinations`
- `combinatorics.py` – `generate_power_set`
- `grid_engine.py` – `build_parameter_grid`, `merge_focused_ranges_into_base_grid`
- `varied_params.py` – `resolve_varied_params`
- `result_builders.py` – `create_result_dict`, `create_error_result_dict`
- `result_selection.py` – `get_best_variant`, `get_top_n_variants`, `filter_results`
- `pareto_frontier.py` – `get_pareto_frontier`

## Public API

- Constants: `GRID_SEARCH_TYPE_*`, `SEARCH_TYPE_*`, `RESULTS_FILE_GRIDSEARCH`, etc.
- `calculate_total_combinations`, `generate_param_combinations`, `generate_power_set`
- `build_parameter_grid`, `merge_focused_ranges_into_base_grid`
- `resolve_varied_params`
- `create_result_dict`, `create_error_result_dict`
- `get_best_variant`, `get_top_n_variants`, `filter_results`, `get_pareto_frontier`

## Dependencies

stdlib only (itertools, typing).

## Usage Example

```python
from level_0 import calculate_total_combinations, generate_param_combinations, create_result_dict

grid = {"lr": [0.01, 0.1], "batch": [32, 64]}
total = calculate_total_combinations(grid)  # 4
result = create_result_dict(
    variant_index=0, variant_id="v0", cv_score=0.85,
    fold_scores=[0.82, 0.88], batch_size_used=32, batch_size_reduced=False,
    variant_specific_data={"lr": 0.01}
)
```
