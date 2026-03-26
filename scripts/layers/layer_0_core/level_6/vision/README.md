# level_6.vision

## Purpose

Vision model registry utilities that load model configuration from an optional JSON-backed registry.

## Contents

| Module | Description |
|--------|-------------|
| `vision_model_registry.py` | Registry helpers for reading model configs and model names |
| `__init__.py` | Package exports for registry helpers |

## Public API

| Name | Description |
|------|-------------|
| `get_vision_model_config` | Return config dict for a registered vision model name |
| `list_vision_models` | Return all registered model names |
| `VISION_MODELS` | Lazy attribute that returns the full registry mapping via `__getattr__` |

## Registry Behavior

- Registry path: `level_6/config/default_configs.json`
- The config file is optional.
- If missing, registry creation succeeds with empty data:
  - `get_vision_model_config(...)` returns `{}` for unknown models
  - `list_vision_models()` returns `[]`

## Dependencies

- **level_5**: `create_json_model_registry`

## Usage Example

```python
from level_6.vision import get_vision_model_config, list_vision_models

models = list_vision_models()
config = get_vision_model_config("dinov2")
```
