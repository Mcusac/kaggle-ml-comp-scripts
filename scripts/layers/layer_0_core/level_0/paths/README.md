# Paths

Pure filesystem path utilities.

## Purpose

Directory creation, path normalization, file size queries, and fold-specific checkpoint/model paths. No dependency on execution environment.

## Contents

- `filesystem.py` – ensure_dir, normalize_path, get_file_size_mb, ensure_file_dir
- `fold_paths.py` – get_fold_checkpoint_path, get_fold_regression_model_path

## Public API

- `ensure_dir` – Create directory (and parents) if needed
- `normalize_path` – Resolve .., ., expand ~, make absolute
- `get_file_size_mb` – File size in MB
- `ensure_file_dir` – Ensure parent dir of a file exists
- `get_fold_checkpoint_path` – Path to fold checkpoint (best_model.pth)
- `get_fold_regression_model_path` – Path to fold regression model (regression_model.pkl)

## Dependencies

stdlib only (pathlib, typing).

## Usage Example

```python
from layers.layer_0_core.level_0 import ensure_dir, normalize_path, ensure_file_dir

output = ensure_dir("output/models")
path = normalize_path("~/data/../models")
ensure_file_dir("output/models/v1/checkpoint.pth")
```
