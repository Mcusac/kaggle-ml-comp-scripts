# search.variants

## Purpose

Variant grid generation, parameter grid resolution, execution logging, and best-score tracking
for grid search runs.

## Contents

- `augmentation_variants.py` — Generates all preprocessor × augmenter variant combinations
  via power-set product.
- `param_grid_resolution.py` — Resolves the correct parameter grid from a grid config dict
  based on mode and ontology.
- `execution_logging.py` — Logs a separator header at the start of each variant run.
- `scoring.py` — Pure function that returns the better of two scores and its associated result.

## Public API

- `generate_variant_grid(preprocessors, augmenters, excluded_preprocessors)` — Returns the
  cartesian product of all preprocessor and augmenter power-set combinations.
- `get_param_grid(grid_config, quick_mode, ontology)` — Resolves and returns the appropriate
  parameter grid from a config dict.
- `log_variant_header(variant_index, total_variants, variant_info)` — Logs a formatted separator
  marking the start of a variant run.
- `select_best_score(current_best_score, new_score, new_result)` — Returns the better score and
  its result, or the unchanged best and `None` if there is no improvement.

## Dependencies

- `level_0.grid_search` — `generate_power_set` for augmentation combinatorics.
- `level_0.runtime` — `get_logger` for structured logging.
- `level_0.errors` — `ConfigValidationError` for misconfigured grids.

## Usage Example
```python
from search.variants import get_param_grid, select_best_score

grid = get_param_grid(config["grid"], quick_mode=True)
best_score, best_result = select_best_score(best_score, score, result)
```