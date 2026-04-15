# guards

## Purpose
Pure invariant enforcement utilities. Guards check structural or data invariants and raise a typed error on violation. They return `None` on success and accept no side effects.

Contract:
- Raise on failure, return `None` on success
- No logging, no orchestration, no domain logic

## Contents
- `arrays.py` — `check_array_finite`: raises if array contains NaN or Inf
- `collections.py` — `check_min_collection_length`: raises if collection is too short
- `config.py` — `validate_config_section_exists`: raises if config attribute is missing or None; `validate_grid_search_config`: raises if config lacks `paths` section
- `none.py` — `check_not_none`: raises if value is None

## Public API
- `check_array_finite(array, *, name)` → None or raises `DataValidationError`
- `check_min_collection_length(collection, min_length, *, name)` → None or raises `DataValidationError`
- `validate_config_section_exists(config, section_name, *, config_name)` → None or raises `ConfigValidationError`
- `validate_grid_search_config(config)` → None or raises `ConfigValidationError`
- `check_not_none(value, name)` → None or raises `DataValidationError`

## Dependencies
- `level_0` — `DataValidationError`, `ConfigValidationError`

## Usage Example
```python
from layers.layer_0_core.level_1.guards import check_array_finite, validate_config_section_exists
check_array_finite(features, name="train_features")
validate_config_section_exists(config, "paths")
```