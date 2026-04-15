# level_1/features/cache

## Purpose
Runtime configuration and filename encoding for the feature cache. Path provider and model ID map are injected by the contest layer at startup.

## Contents
- `config.py` — `set_feature_cache_path_provider`, `set_model_id_map`, `get_cache_base_paths`, `get_model_name_from_model_id`, `get_metadata_dir`
- `filename.py` — `generate_feature_filename`, `parse_feature_filename`

## Public API
- `set_feature_cache_path_provider(provider)` — register path provider; must be called at startup
- `set_model_id_map(model_id_map)` — register model name → ID map; must be called at startup
- `get_cache_base_paths()` → `(input_base, working_base)`
- `get_model_name_from_model_id(model_id)` → model name string
- `get_metadata_dir()` → metadata directory path or None
- `generate_feature_filename(model_id, combo_id)` → filename string
- `parse_feature_filename(filename)` → `(model_id, combo_id)`

## Dependencies
- `level_0` — `get_logger`

## Usage Example
```python
from layers.layer_0_core.level_1.features import set_feature_cache_path_provider, set_model_id_map, generate_feature_filename

set_feature_cache_path_provider(lambda: my_paths)
set_model_id_map({"model_a": "m1", "model_b": "m2"})
filename = generate_feature_filename("m1", "combo_0")
```
