# model_io

## Purpose

Model save/load for PyTorch, scikit-learn, and generic pickle. Regression model saver for feature extraction trainers.

## Contents

- **model_io.py**: save_model_raw, save_model, load_model_raw, load_model
- **model_saver_helper.py**: save_regression_model

## Public API

- `save_model_raw(model, path, metadata=None)` — Save without validation
- `save_model(model, path, metadata=None)` — Save with validation and logging
- `load_model_raw(path)` — Load without validation, returns (model, metadata)
- `load_model(path)` — Load with validation
- `save_regression_model(model, save_dir)` — Save regression model + metadata to fold dir

## Dependencies

- level_0: ModelError, ModelLoadError, ensure_dir, get_logger, get_torch, is_torch_available
- level_3: validate_file_exists
- level_4: load_json, load_pickle, save_json, save_pickle

## Usage Example

```python
from level_5 import save_model, load_model, save_regression_model
from pathlib import Path

save_model(model, Path("output/model.pth"), metadata={"epoch": 10})
model, meta = load_model("output/model.pth")

save_regression_model(ridge_model, Path("output/fold_0"))
```
