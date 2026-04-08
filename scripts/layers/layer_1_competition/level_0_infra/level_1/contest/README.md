---
generated: 2026-04-08
---

# infra/level_1/contest — Shared contest CLI and data loading

**Import:** `layers.layer_1_competition.level_0_infra.level_1.contest` or symbols from the parent `level_1` package root.

## Purpose

Provides contest-agnostic argparse helpers, context construction, CSV loading, train/validation splits, and lightweight pipeline orchestration shells re-exported from core for competition entrypoints.

## Contents

| Module | Description |
|--------|-------------|
| `argparse_builders` | Reusable argparse flags for training, models, ensemble, output paths |
| `cli` | Common contest CLI arguments and parsing helpers |
| `context` | `ContestContext` and `build_contest_context` backed by the infra registry |
| `csv_io` | Training CSV load with contest-registered loader hooks |
| `data_loading` | Facade: `load_contest_data`, `load_contest_training_data` |
| `splits` | Train/validation splitting and K-fold wiring |

## Public API

Symbols listed in `contest/__init__.py` `__all__`: CLI and parsing helpers, `ContestContext`, loaders, splitters, argparse builders, and `BasePipeline` / validate-first shell types (`ValidateFirstRunner`, `ValidateFirstPipelineResultShell`, `TwoStageValidateFirstPipelineResultShell`) sourced from `layers.layer_0_core.level_1.pipelines`.

## Dependencies

- **`layers.layer_0_core.level_0`**, **`level_4`**, **`level_1`** (pipelines): logging, CSV I/O, orchestration shells
- **`layers.layer_1_competition.level_0_infra.level_0`**: re-exported types are not imported directly here; context/registry use infra contracts
- **`layers.layer_1_competition.level_0_infra.level_1.registry`**: contest registration lookup (in `data_loading` via explicit submodule import to avoid package cycles)

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import (
    add_common_contest_args,
    build_contest_context,
    load_contest_data,
)

ctx = build_contest_context("my_contest")
train, val, test = load_contest_data("my_contest", model_type="tabular")
```
