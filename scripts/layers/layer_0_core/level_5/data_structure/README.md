# data_structure

## Purpose

Provides configuration loaders, JSON model registry, and tabular model base classes for vision and tabular pipelines.

## Contents

- **base/**: JSONConfigLoader, create_json_model_registry
- **tabular/**: BaseTabularModel, SparseTabularDataset

## Public API

- `JSONConfigLoader` — Load JSON config with lowercase keys
- `create_json_model_registry(config_path)` — Returns (get_config, list_models, get_all) for lazy-loaded model catalog
- `BaseTabularModel` — Abstract base for tabular models (fit, predict, predict_proba, save, load)
- `SparseTabularDataset` — PyTorch Dataset for sparse multi-label with memmap support

## Dependencies

- level_0: get_logger, ensure_file_dir, get_torch
- level_4: load_json, save_pickle, load_pickle

## Usage Example

```python
from level_5 import JSONConfigLoader, create_json_model_registry, BaseTabularModel
from pathlib import Path

loader = JSONConfigLoader("model_config", config_dir="config")
value = loader.get("learning_rate")

get_config, list_models, get_all = create_json_model_registry(Path("models.json"))
config = get_config("ridge")
```
