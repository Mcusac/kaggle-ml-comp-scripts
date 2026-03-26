# data_structure.base

## Purpose

Configuration loading and JSON model registry for domain-specific model catalogs.

## Contents

- **config_loader.py**: JSONConfigLoader
- **json_model_registry.py**: create_json_model_registry

## Public API

- `JSONConfigLoader(config_name, config_dir="config", lowercase_keys=True)` — Load JSON config from config_dir/{config_name}.json
- `create_json_model_registry(config_path)` — Returns (get_config, list_models, get_all) for lazy-loaded catalog

## Dependencies

- level_0: get_logger
- level_4: load_json

## Usage Example

```python
from level_5 import JSONConfigLoader, create_json_model_registry
from pathlib import Path

loader = JSONConfigLoader("training")
lr = loader.get("learning_rate")

get_config, list_models, _ = create_json_model_registry(Path("vision_models.json"))
for name in list_models():
    cfg = get_config(name)
```
