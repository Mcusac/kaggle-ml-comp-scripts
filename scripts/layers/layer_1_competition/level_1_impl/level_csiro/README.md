# CSIRO contest package (`level_csiro`)

Implementation of the CSIRO Biomass competition under `layers.layer_1_competition.level_1_impl`. Code is split into **dependency layers** `level_0` … `level_7`: a module in `level_K` must only import other CSIRO modules from `level_X` with `X < K` (using fully qualified paths such as `layers.layer_1_competition.level_1_impl.level_csiro.level_2.variant_selection`).

## Layout

| Directory | Role |
|-----------|------|
| `level_0` | Config, paths, metrics, biomass helpers, shared CLI args, export hooks |
| `level_1` | Training/test pipelines, modeling shim, stacking helpers, variant metadata |
| `level_2` | Feature/regression pipelines, stacking, submit flows, variant/gridsearch metadata IO |
| `level_3` | Variant selection, ensemble glue, regression OOF helpers, training result persistence (`__init__` re-exports only this level) |
| `level_4` | Feature extraction setup, grid-search context, ensemble handlers, hybrid stacking pipeline |
| `level_5` | Grid/submit/stacking/training CLI handlers (`handlers_*`, `regression_training`) |
| `level_6` | `train_and_export_pipeline` (train/export orchestration used by handlers and multi-variant flows) |
| `level_7` | CLI facade: `extend_subparsers`, `get_handlers`, **all** `handle_*` entrypoints, `multi_variant_regression_training_pipeline`, and `handlers_multi_variant` (see `level_7/__init__.py` `__all__`) |

### Notable `level_csiro.level_0` modules

Integration and CLI glue often touch: `aggregate.py` (training data loader for registration), `data_schema.py`, `config.py`, `paths.py`, `handlers_common.py`, `metrics.py`, `model_constants.py`, `export_ops.py`, `checkpoint_utils.py`, plus biomass and stacking helpers (`biomass_models.py`, `stacking_utils.py`, etc.).

## Package root and registration

- **Root `__init__.py`**: re-exports the **concatenation** of every sub-level’s `__all__`. Using `from layers.layer_1_competition.level_1_impl.level_csiro import *` pulls a **very large** namespace. Prefer `layers.layer_1_competition.level_1_impl.level_csiro.level_K` or a concrete submodule for new code.
- **`registration.py`**: importing `level_csiro` runs **import-time side effects**: `set_model_id_map` (global feature cache) and `register_contest` (contest registry). Tests or tools that need isolation should mock these or import submodules without loading `registration` unless intentional.

## Imports

- **`__init__.py` policy**: each `level_K/__init__.py` re-exports only symbols defined under that same `level_K` package. Do not pull APIs from `level_2` into `level_3/__init__.py` (or any cross-level barrel). Import stacking and similar from `layers.layer_1_competition.level_1_impl.level_csiro.level_2…` (or the submodule path) at the call site.
- **Inside `level_csiro`**: prefer explicit submodule imports (e.g. `layers.layer_1_competition.level_1_impl.level_csiro.level_1.train_pipeline`) so names resolve without relying on another level’s `__init__.py`.
- **Global script tree**: `from level_0 import ...`, `from level_3 import ...`, etc. refer to top-level `scripts/level_*` on `PYTHONPATH`, not CSIRO sub-packages. Files under `level_csiro/level_2/` are especially easy to misread when both appear—see comments in those modules where global `level_2` is used.

## Running

Set `PYTHONPATH` to the `scripts` directory (same layout as `run.py` / `path_bootstrap`), then run the main CLI entrypoint for your project.
