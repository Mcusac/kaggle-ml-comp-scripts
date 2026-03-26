# infra/level_0 — Competition infra base

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_0/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_0` (with `scripts/` on `sys.path` via `path_bootstrap`).

## Purpose

Abstract base classes and shared utilities for Kaggle contest implementations: contest contract (config, paths, data schema, post-processing), CLI parser helpers, path utilities, model metadata helpers, and pipeline kwargs / training config.

**Registry, export handlers, contest CLI/context (`build_contest_context`, `resolve_data_root_from_args`), and environment path helpers (`get_data_root_path`, …) live on `layers.layer_1_competition.level_0_infra.level_1`.**

## Package layout

| Subpackage / area | Contents |
|-------------------|----------|
| `abstractions/` | `ContestInputValidator`, `ContestMetric`, `ContestPipelineProtocol` |
| `contest/` | `ContestConfig`, `ContestDataSchema`, `ContestPaths`, `ContestPostProcessor`, `ClipRangePostProcessor`, `ContestOntologySystem`, `ContestHierarchy`, `ContestPathConfig` |
| `cli/` | `parser_helpers` — `add_grid_search_parsers`, `add_training_parsers`, `add_ensemble_parsers`, `add_submission_parsers` |
| `features/` | `validate_feature_extraction_inputs` |
| `model/` | `model_constants`, feature-extraction getters, `detect_model_type`, `feature_catalog`, `embeddings`, `verify_export_output` |
| `paths/` | `is_kaggle_input`, `resolve_data_root`, `load_feature_filename_from_gridsearch` |
| `pipeline/` | `create_pipeline_kwargs`, `create_training_config` |

## Public API

Union of subpackage `__all__` values on the root `__init__.py` (contest abstractions, CLI parsers, features validator, model/path/pipeline symbols). For **`get_contest`**, **`build_contest_context`**, **`resolve_data_root_from_args`**, **`get_data_root_path`**, **`get_output_path`**, export handlers, and registry types — import from **`layers.layer_1_competition.level_0_infra.level_1`**.

## Dependencies

- **General `level_0`–`level_2`:** as required by individual modules (see precheck / architecture rules for upward imports).

## Usage example

```python
from layers.layer_1_competition.level_0_infra.level_0 import (
    ContestPaths,
    is_kaggle_input,
    get_pretrained_weights_path,
)
from layers.layer_1_competition.level_0_infra.level_1 import (
    build_contest_context,
    get_contest,
)

ctx = build_contest_context("csiro")
paths = ctx.get_paths()
config = ctx.get_config()

if is_kaggle_input("/kaggle/input/csiro-biomass"):
    data_root = str(paths.local_data_root)
```
