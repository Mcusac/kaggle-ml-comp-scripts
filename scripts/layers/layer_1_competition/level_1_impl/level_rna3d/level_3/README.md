# RNA3D level_3

## Purpose

Orchestrates multi-model training for the RNA3D contest: validates inputs, resolves output paths, and invokes tier-2 registered trainers for each requested model name.

## Contents

- **training/** — Implementation package for the training pipeline (`pipeline.py`).

## Public API

| Name | Description |
|------|-------------|
| train_pipeline | Validate `data_root`, train each named model via tier-2 registry, write artifacts under contest output. |

## Dependencies

- **level_0** — `get_logger`, `ensure_dir` for logging and filesystem setup.
- **layers.layer_1_competition.level_1_impl.level_rna3d.level_0** — `validate_rna3d_inputs`, `RNA3DPaths` for data checks and output layout.
- **layers.layer_1_competition.level_1_impl.level_rna3d.level_2** — `get_trainer`, `list_available_models` for model registration and trainer lookup.

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_rna3d.level_3 import train_pipeline

train_pipeline(
    data_root="/path/to/competition/data",
    train_mode="end_to_end",
    models=["baseline_approx"],
)
```
