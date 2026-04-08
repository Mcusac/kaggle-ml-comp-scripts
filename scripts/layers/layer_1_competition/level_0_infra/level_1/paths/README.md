---
generated: 2026-04-08
---

# infra/level_1/paths — Contest path resolution

**Import:** `layers.layer_1_competition.level_0_infra.level_1` or `…level_1.paths`.

## Purpose

Resolves data roots, run directories, model trees, submission paths, and Kaggle-vs-local behavior for contest tooling using `ContestPaths` from infra level_0.

## Contents

| Module | Description |
|--------|-------------|
| `env_paths` | `get_run_py_path`, `get_data_root_path` |
| `models` | `contest_models_dir`, `contest_model_dir` |
| `output_roots` | `contest_output_root` |
| `path_utils` | `resolve_data_root` |
| `runs` | `contest_runs_root`, `contest_run_dir` |
| `submissions` | `contest_submission_path` |

## Public API

See `paths/__init__.py` `__all__`: path helpers plus `is_kaggle_input` from `layers.layer_0_core.level_0`.

## Dependencies

- **`layers.layer_0_core.level_0`**: `is_kaggle_input`
- **`layers.layer_1_competition.level_0_infra.level_0`**: `ContestPaths`, `contest_models_dir`
- **`layers.layer_1_competition.level_0_infra.level_1.registry`**: contest registry for default roots (`env_paths`)

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import (
    get_data_root_path,
    contest_models_dir,
)
from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths

paths = ContestPaths()
root = get_data_root_path()
models = contest_models_dir(paths, "my_contest")
```
