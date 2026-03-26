# RNA3D `level_4`

## Purpose

Exposes argparse-driven CLI entrypoints for **train**, **tune**, and **submit**, wiring namespace objects into the lower-tier RNA3D pipelines.

## Contents

| Module | Role |
|--------|------|
| `handlers.py` | Implements `train`, `tune`, `submit`, and `get_handlers()` mapping subcommand names to callables. |

## Public API

Symbols re-exported from `__init__.py`:

| Name | Description |
|------|-------------|
| `train` | Runs `train_pipeline` from tier 3 using `args.data_root`, `args.train_mode` (default `end_to_end`), and `args.models`. |
| `tune` | Runs `tune_pipeline` from tier 2 using tuning-related fields on `args`. |
| `submit` | Runs `submit_pipeline` from tier 2 using submission-related fields on `args`. |
| `get_handlers` | Returns `{"train": train, "tune": tune, "submit": submit}` for contest CLI registration. |

## Dependencies

- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_2`** — `tune_pipeline` and `submit_pipeline` for hyperparameter search and submission assembly.
- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_3`** — `train_pipeline` for model training orchestration.

## Usage Example

```python
import argparse

from layers.layer_1_competition.level_1_impl.level_rna3d.level_4 import get_handlers

handlers = get_handlers()
ns = argparse.Namespace(
    data_root="/path/to/data",
    train_mode="end_to_end",
    models=["baseline_approx"],
)
handlers["train"](ns)
```

Consumers may also import `get_handlers` from `layers.layer_1_competition.level_1_impl.level_rna3d` if the contest root package re-exports tier 4.
