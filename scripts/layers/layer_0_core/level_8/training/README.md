# level_8.training

## Purpose

Training pipelines and workflows for vision and tabular models: single-run training, k-fold cross-validation, train-and-export, robust CV splits, and train/export mode detection.

## Contents

| Module | Description |
|--------|-------------|
| `train_pipeline.py` | Atomic training pipeline for vision and tabular models |
| `cross_validate.py` | K-fold cross-validation workflow |
| `train_and_export.py` | Workflow that trains a model and exports it for submission |
| `cv_splits.py` | Robust CV splits via visual clustering or hierarchical stratification |
| `detect_train_export_mode.py` | Train/export mode detection and grid search results resolution |

## Public API

| Name | Description |
|------|-------------|
| `TrainPipeline` | Atomic pipeline for training vision or tabular models |
| `CrossValidateWorkflow` | K-fold cross-validation workflow |
| `TrainAndExportWorkflow` | Train then export workflow |
| `create_robust_cv_splits` | Create CV splits using visual clustering or hierarchical stratification |
| `detect_train_export_mode` | Detect train/export mode and resolve grid search results path |

## Dependencies

- **level_0**: ensure_dir, get_logger
- **level_1**: BasePipeline, validate_config_section_exists, get_device, print_config_section
- **level_2**: create_optimizer, create_scheduler, create_loss_function
- **level_4**: create_vision_model, save_pickle, create_dataloaders, EvaluatePipeline
- **level_5**: ExportPipeline
- **level_6**: VisionTrainer, PredictPipeline
- **level_7**: create_tabular_model, auto_detect_grid_search_results

## Usage Example

```python
from level_8 import TrainPipeline, CrossValidateWorkflow

pipeline = TrainPipeline(config=config, model_type="vision", train_data=train_df, val_data=val_df)
result = pipeline.run()

cv_workflow = CrossValidateWorkflow(config=config, model_type="tabular", n_folds=5, X=X, y=y)
cv_result = cv_workflow.run()
```
