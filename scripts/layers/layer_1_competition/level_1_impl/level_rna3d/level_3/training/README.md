# RNA3D level_3 — training

## Purpose

Holds the implementation of the tier-3 training orchestration entrypoint used by the parent `level_3` package.

## Contents

- **pipeline.py** — `train_pipeline`: validation loop over requested models and trainer invocation.

## Public API

| Name | Description |
|------|-------------|
| train_pipeline | Same as re-exported from `layers.layer_1_competition.level_1_impl.level_rna3d.level_3`. |

## Dependencies

- **level_0** — `get_logger`, `ensure_dir`.
- **layers.layer_1_competition.level_1_impl.level_rna3d.level_0** — `validate_rna3d_inputs`, `RNA3DPaths`.
- **layers.layer_1_competition.level_1_impl.level_rna3d.level_2** — `get_trainer`, `list_available_models`.

## Usage Example

Prefer importing from the tier barrel:

```python
from layers.layer_1_competition.level_1_impl.level_rna3d.level_3 import train_pipeline

train_pipeline(
    data_root="/path/to/competition/data",
    train_mode="end_to_end",
    models=["baseline_approx"],
)
```
