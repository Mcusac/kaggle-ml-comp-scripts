# level_8

## Purpose

Level 8 owns atomic training (`TrainPipeline`), robust CV splits, train/export mode detection, dataset grid search (`DatasetGridSearch`), regression grid-search helpers (`run_regression_cv_fold`, variant result builders), and regression model ensembling.

## Contents

| Package | Description |
|---------|-------------|
| `training/` | `TrainPipeline`, `create_robust_cv_splits`, `detect_train_export_mode` |
| `regression/` | Regression CV fold runner, variant result dicts, `RegressionEnsemble` |
| `grid_search/` | `DatasetGridSearch`, end-to-end variant config extraction and result builders |

## Public API

Exports are composed from sub-packages (`grid_search`, `regression`, `training`). Names include:

| Name | Description |
|------|-------------|
| `TrainPipeline` | Atomic training for vision or tabular models |
| `create_robust_cv_splits` | CV splits via embedding clusters or hierarchical stratification |
| `detect_train_export_mode` | Resolve grid search results path and print mode summary |
| `DatasetGridSearch` | Grid search over dataset preprocessing/augmentation variants |
| `extract_variant_config` | Extract per-variant config for end-to-end grid search |
| `create_end_to_end_variant_result` | Build standardized result dict for an end-to-end variant |
| `run_regression_cv_fold` | Single CV fold for a regression model on pre-extracted features |
| `create_regression_variant_result` | Build standardized result dict for a regression variant |
| `RegressionEnsemble` | Loaded regression models with configurable combination |
| `create_regression_ensemble_from_paths` | Factory for `RegressionEnsemble` from paths and configs |

## Dependencies

- **level_0**: Logging, paths, config validation, grid search constants, ensembling types
- **level_1**: Pipelines, config validation, device, variant grid, feature splits, config printing
- **level_2**: Optimizer, scheduler, loss
- **level_3**: Regression model factory
- **level_4**: Vision model, dataloaders, pickle I/O
- **level_5**: `VisionTrainer`
- **level_6**: Grid search base, variant keys, default hyperparameters, `SimpleAverageEnsemble`
- **level_7**: Variant execution, result builders, ensembling factory, tabular model factory, grid search auto-detect

## Usage Example

```python
from level_8 import TrainPipeline, create_robust_cv_splits

# Train a vision model (typical kwargs: train_data, val_data, image_dir, target_cols)
pipeline = TrainPipeline(
    config=config,
    model_type="vision",
    train_data=train_df,
    val_data=val_df,
    image_dir=image_dir,
    target_cols=["target"],
)
pipeline.setup()
result = pipeline.execute()
pipeline.cleanup()

# Tabular-style CV splits on a DataFrame
split_df = create_robust_cv_splits(
    data=df,
    target_names=["y1", "y2"],
    target_weights={"y1": 0.5, "y2": 0.5},
    n_splits=5,
)
```
