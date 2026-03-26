# level_9.grid_search

## Purpose

Grid search pipelines for dataset variants, regression hyperparameters, and vision/tabular hyperparameters. Orchestrates level_6 GridSearchBase and level_7/8 components.

## Contents

| Module | Description |
|--------|-------------|
| `dataset_grid_search_pipeline.py` | Dataset grid search, test_max_augmentation, attach_paths_to_config, SimplePaths |
| `regression_grid_search.py` | RegressionGridSearch class and regression_grid_search_pipeline |
| `hyperparameter.py` | HyperparameterGridSearch for vision/tabular hyperparameter tuning |

## Public API

| Name | Description |
|------|-------------|
| `attach_paths_to_config` | Attach SimplePaths wrapper to config for data_root access without contest import |
| `dataset_grid_search_pipeline` | Run dataset grid search over preprocessing/augmentation variants |
| `test_max_augmentation_pipeline` | Test maximally augmented dataset variant (requires train_pipeline_fn in kwargs) |
| `HyperparameterGridSearch` | Grid search for vision/tabular hyperparameter optimization |
| `RegressionGridSearch` | Grid search for regression model hyperparameters |
| `regression_grid_search_pipeline` | Run regression grid search using contest_context |

## Dependencies

- **level_0**: get_logger, ensure_dir, create_error_result_dict, BEST_VARIANT_FILE_DATASET, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION
- **level_4**: save_json, EvaluatePipeline
- **level_6**: GridSearchBase, PredictPipeline, create_variant_specific_data, create_regression_variant_key_from_result
- **level_7**: HyperparameterGridSearchBase
- **level_8**: DatasetGridSearch, TrainPipeline, run_regression_cv_fold, create_regression_variant_result

## Usage Example

```python
from level_9 import attach_paths_to_config, regression_grid_search_pipeline

# Regression grid search (contest provides contest_context)
regression_grid_search_pipeline(
    contest_context,
    feature_filename="variant_0100_features.npz",
    regression_model_type="lgbm",
    search_type="quick",
)
```
