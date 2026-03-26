# infra/level_1/grid_search — Contest grid search base and context

**On disk:** `…/level_0_infra/level_1/grid_search/`. **Import:** `layers.layer_1_competition.level_0_infra.level_1` (symbols may also appear on `layers.layer_1_competition.level_0_infra.level_3` where re-exported).

## Purpose

Provides contest-aware grid search infrastructure: a base class that injects contest paths and config, and a context builder for orchestration pipelines.

## Contents
| Module | Description |
|---|---|
| `base` | `ContestGridSearchBase` — extends `GridSearchBase` with contest injection. |
| `context` | `build_grid_search_context` — builds context with paths, config, and injected overrides. |

## Public API
| Name | Description |
|---|---|
| `ContestGridSearchBase` | Contest-aware grid search base. Subclasses pass `contest_name` and implement `_generate_variant_grid`, `_run_variant`, `_create_variant_key`. |
| `build_grid_search_context` | Returns a context object with `get_paths`, `get_config`, `get_metric_calculator`, `get_data_schema`, `get_post_processor`, `get_test_pipeline`, `load_regression_gridsearch_results`, `get_metadata_handler`, `get_feature_cache_loader`, `get_parameter_grid_fn`. |

## Dependencies
| Level | Reason |
|---|---|
| `level_0` | `get_logger`. |
| `level_6` | `GridSearchBase`. |
| `infra level_0` | `get_contest`. |

## Usage Example
```python
from layers.layer_1_competition.level_0_infra.level_3 import build_grid_search_context, ContestGridSearchBase

# Context
ctx = build_grid_search_context("csiro", metric_calculator=calc_fn)
paths = ctx.get_paths()

# Base class (subclass in contest layer)
class CsiroGridSearch(ContestGridSearchBase):
    def __init__(self, config, **kwargs):
        super().__init__(config, "hyperparameter", "csiro", **kwargs)

    def _generate_variant_grid(self): ...
    def _run_variant(self, variant, idx): ...
    def _create_variant_key(self, variant): ...
```
