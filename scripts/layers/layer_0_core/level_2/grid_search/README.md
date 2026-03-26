# grid_search

Grid search environment setup, parameter grid resolution, and variant result accumulation.

## Purpose

Provides the infrastructure for running hyperparameter and dataset grid searches: sets up the execution environment, resolves keyed parameter grids from config, and accumulates variant results for comparison.

## Contents

- `environment_setup.py` — `setup_grid_search_environment`, `apply_memory_optimizations`, `normalize_base_model_dir`, `create_grid_search_dir`
- `param_grid.py` — `resolve_keyed_param_grid`: resolve parameter grids with named keys from config
- `variant_accumulator.py` — `accumulate_variant_results`: run and collect results across grid variants

## Public API

- `setup_grid_search_environment(config)` — Initialize device, log GPU info, and return device object for grid search runs
- `apply_memory_optimizations()` — Apply memory-saving settings for GPU environments
- `normalize_base_model_dir(base_dir)` — Ensure base model directory exists and is normalized
- `create_grid_search_dir(base_dir, grid_search_type)` — Create and return the grid search output directory
- `resolve_keyed_param_grid(config, search_type)` — Resolve the parameter grid for a named search type from config
- `accumulate_variant_results(variants, executor, config)` — Execute all grid variants and return accumulated results

## Dependencies

- **level_0** — `ensure_dir`, `ConfigValidationError`, `get_logger`
- **level_1** — `get_device`, `get_device_info`, `execute_variants`, `resolve_param_grid`

## Usage Example

```python
from level_2.grid_search import setup_grid_search_environment, resolve_keyed_param_grid

device = setup_grid_search_environment(config)
param_grid = resolve_keyed_param_grid(config, search_type="hyperparameter")
```
