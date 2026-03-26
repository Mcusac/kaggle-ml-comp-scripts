# level_8

## Purpose

Level 8 provides training pipelines, cross-validation workflows, train-and-export workflows, dataset grid search, regression ensemble, and variant helpers for ML competition orchestration.

## Contents

| Package | Description |
|---------|-------------|
| `training/` | TrainPipeline, CrossValidateWorkflow, TrainAndExportWorkflow, cv_splits, detect_train_export_mode |
| `regression/` | Regression variant execution and ensemble |
| `grid_search/` | Dataset grid search and end-to-end variant helpers |

## Public API

| Name | Description |
|------|-------------|
| `TrainPipeline` | Atomic pipeline for training vision or tabular models |
| `CrossValidateWorkflow` | K-fold cross-validation workflow |
| `create_robust_cv_splits` | Create CV splits using visual clustering or hierarchical stratification |
| `TrainAndExportWorkflow` | Train then export workflow |
| `detect_train_export_mode` | Detect train/export mode and resolve grid search results path |
| `run_regression_cv_fold` | Run a single CV fold for regression model |
| `create_regression_variant_result` | Build result dict for regression variant |
| `extract_variant_config` | Extract config from variant for end-to-end grid search |
| `create_end_to_end_variant_result` | Build result dict for end-to-end variant |
| `RegressionEnsemble` | Ensemble of regression models with weighted combination |
| `create_regression_ensemble_from_paths` | Create RegressionEnsemble from model paths |
| `DatasetGridSearch` | Grid search over dataset preprocessing/augmentation variants |

## Dependencies

- **level_0**: Logging, paths, config validation, ensembling method
- **level_1**: BasePipeline, validation, variant grid, split features
- **level_2**: Optimizer, scheduler, loss
- **level_3**: Regression model creation
- **level_4**: Vision model, dataloaders, EvaluatePipeline, save_pickle
- **level_5**: ExportPipeline
- **level_6**: VisionTrainer, PredictPipeline, GridSearchBase, variant keys, SimpleAverageEnsemble
- **level_7**: Tabular model, build_success_result, build_error_result, run_single_variant, create_ensembling_method, auto_detect_grid_search_results

## Usage Example

```python
from level_8 import TrainPipeline, CrossValidateWorkflow

# Single training run
pipeline = TrainPipeline(
    config=config,
    model_type="vision",
    train_data=train_df,
    val_data=val_df,
    image_dir=image_dir,
    target_cols=["target"],
)
result = pipeline.run()

# Cross-validation
cv_workflow = CrossValidateWorkflow(
    config=config,
    model_type="tabular",
    n_folds=5,
    X=X_train,
    y=y_train,
)
cv_result = cv_workflow.run()
```
