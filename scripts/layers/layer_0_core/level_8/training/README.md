# level_8.training

## Purpose

Atomic vision/tabular training (`TrainPipeline`), robust CV split construction, and helper to detect train vs export mode from grid-search results.

## Contents

| Module | Description |
|--------|-------------|
| `train_pipeline.py` | `TrainPipeline` (vision or tabular) |
| `cv_splits.py` | `create_robust_cv_splits` (cluster- or hierarchy-based folds) |
| `detect_train_export_mode.py` | `detect_train_export_mode` |

## Public API

| Name | Description |
|------|-------------|
| `TrainPipeline` | Setup/execute/cleanup training for vision or tabular models |
| `create_robust_cv_splits` | Add a `fold` column using embeddings or hierarchical keys |
| `detect_train_export_mode` | Auto-detect grid search results and print mode banner |

## Dependencies

- **level_0**: `ensure_dir`, `get_logger`
- **level_1**: `BasePipeline`, `validate_config_section_exists`, `get_device`, `print_config_section`
- **level_2**: `create_optimizer`, `create_scheduler`, `create_loss_function`
- **level_4**: `create_vision_model`, `save_pickle`, `create_dataloaders`
- **level_5**: `VisionTrainer`
- **level_6**: `auto_detect_grid_search_results`
- **level_7**: `create_tabular_model`

## Usage Example

```python
from layers.layer_0_core.level_8 import TrainPipeline, detect_train_export_mode

results_path = detect_train_export_mode(model_name="my_model", fresh_train=False)

pipeline = TrainPipeline(
    config=config,
    model_type="vision",
    train_data=train_df,
    val_data=val_df,
    image_dir="/data/images",
    target_cols=["label"],
)
pipeline.setup()
out = pipeline.execute()
pipeline.cleanup()
```
