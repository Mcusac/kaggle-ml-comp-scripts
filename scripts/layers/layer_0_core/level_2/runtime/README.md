# runtime

Orchestration-level hardware environment detection.

## Purpose

Queries hardware and environment facts at the start of a pipeline run and returns an execution context dictionary for downstream components.

## Contents

- `environment.py` — `setup_runtime_environment`: detect Kaggle environment and GPU availability

## Public API

- `setup_runtime_environment()` — Returns `Dict[str, Any]` with keys `is_kaggle` (bool), `has_gpu` (bool), `gpu_info` (dict from layers.layer_0_core.level_1's `get_device_info`)

## Dependencies

- **level_0** — `get_logger`, `is_kaggle`
- **level_1** — `get_device_info`

## Usage Example

```python
from layers.layer_0_core.level_2.runtime import setup_runtime_environment

ctx = setup_runtime_environment()
if ctx["has_gpu"]:
    print("GPU available:", ctx["gpu_info"]["device_names"])
```
