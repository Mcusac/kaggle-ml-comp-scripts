# level_9

## Purpose

Level 9 provides hyperparameter grid search, dataset and regression grid-search pipelines, cross-validation and train/export workflows, and train-then-predict orchestration built on level_8. Contest and level_10 code import this package’s public API.

## Contents

| Package | Description |
|---------|-------------|
| `grid_search/` | Dataset grid search, regression hyperparameter search, and vision/tabular hyperparameter grid search |
| `training/` | `CrossValidateWorkflow` and `TrainAndExportWorkflow` composing training, evaluation, and export |
| `train_predict/` | `TrainPredictWorkflow` (train then predict on held-out or test data) |

## Public API

Exported names match `level_9/__init__.py` (`__all__`). Summary:

| Name | Description |
|------|-------------|
| `attach_paths_to_config` | Attach a thin paths wrapper to config so pipelines can read output/model/data paths without importing contest code |
| `dataset_grid_search_pipeline` | Run dataset grid search over preprocessing/augmentation variants |
| `test_max_augmentation_pipeline` | Single-variant smoke run with maximal augmentation |
| `HyperparameterGridSearch` | Grid search over training hyperparameters (vision/tabular) |
| `RegressionGridSearch` | Grid search for regression heads on cached features |
| `regression_grid_search_pipeline` | End-to-end regression grid search driven by `contest_context` |
| `CrossValidateWorkflow` | K-fold cross-validation using `TrainPipeline` / `EvaluatePipeline` / `PredictPipeline` as needed |
| `TrainAndExportWorkflow` | Train then export artifacts via `ExportPipeline` |
| `TrainPredictWorkflow` | Train then run `PredictPipeline` |

## Dependencies

- **level_0**: logging, constants, helpers (`ensure_dir`, `create_error_result_dict`, etc.)
- **level_1**: `BasePipeline`
- **level_4**: `save_json`, `EvaluatePipeline`
- **level_5**: `ExportPipeline`
- **level_6**: `GridSearchBase`, `PredictPipeline`, regression variant helpers
- **level_7**: `HyperparameterGridSearchBase`
- **level_8**: `DatasetGridSearch`, `TrainPipeline`, regression CV and result helpers

## Usage Example

```python
import path_bootstrap

path_bootstrap.prepend_framework_paths()

from layers.layer_0_core.level_9 import dataset_grid_search_pipeline, TrainPredictWorkflow

dataset_grid_search_pipeline(contest_context, train_pipeline_fn=my_train_fn)

workflow = TrainPredictWorkflow(
    config=config,
    model_type="vision",
    train_data=train_df,
    val_data=val_df,
    test_data=test_df,
)
workflow.setup()
result = workflow.execute()
```

## Generated

2026-04-08 (audit pass 1).
