# level_9

## Purpose

Level 9 provides hyperparameter grid search pipelines, dataset grid search orchestration, regression grid search, and the train-then-predict workflow. Consumed by level_10 and contest layers.

## Contents

| Package | Description |
|---------|-------------|
| `grid_search/` | Dataset, regression, and hyperparameter grid search pipelines |
| `train_predict/` | Train-then-predict workflow composing TrainPipeline and PredictPipeline |

## Public API

| Name | Description |
|------|-------------|
| `attach_paths_to_config` | Attach SimplePaths wrapper to config so execution can access data_root without contest import |
| `dataset_grid_search_pipeline` | Run dataset grid search over preprocessing/augmentation variants |
| `test_max_augmentation_pipeline` | Test maximally augmented dataset variant |
| `HyperparameterGridSearch` | Grid search for vision/tabular hyperparameter optimization |
| `RegressionGridSearch` | Grid search for regression model hyperparameters (pre-extracted features) |
| `regression_grid_search_pipeline` | Run regression grid search using contest_context |
| `TrainPredictWorkflow` | Workflow that trains a model then generates predictions |

## Dependencies

- **level_0**: get_logger, ensure_dir, create_error_result_dict, BEST_VARIANT_FILE_DATASET, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION
- **level_1**: BasePipeline
- **level_4**: save_json, EvaluatePipeline
- **level_6**: GridSearchBase, PredictPipeline, create_variant_specific_data, create_regression_variant_key_from_result
- **level_7**: HyperparameterGridSearchBase
- **level_8**: DatasetGridSearch, TrainPipeline, run_regression_cv_fold, create_regression_variant_result

## Usage Example

```python
from level_9 import attach_paths_to_config, dataset_grid_search_pipeline, TrainPredictWorkflow

# Dataset grid search (contest passes contest_context)
dataset_grid_search_pipeline(contest_context, train_pipeline_fn=my_train_fn)

# Train then predict
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
