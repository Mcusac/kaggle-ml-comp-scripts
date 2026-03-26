# level_8.regression

## Purpose

Regression variant execution and ensemble: run CV folds for regression models, build variant result dicts, and combine predictions from multiple regression models.

## Contents

| Module | Description |
|--------|-------------|
| `regression_variant_helpers.py` | CV fold execution and result builders for regression variants |
| `regression_ensemble.py` | Regression model ensemble with weighted combination |

## Public API

| Name | Description |
|------|-------------|
| `run_regression_cv_fold` | Run a single CV fold for regression model |
| `create_regression_variant_result` | Build result dict for regression variant |
| `RegressionEnsemble` | Ensemble of regression models with weighted combination |
| `create_regression_ensemble_from_paths` | Create RegressionEnsemble from model paths |

## Dependencies

- **level_0**: get_logger, EnsemblingMethod
- **level_1**: split_features_by_fold
- **level_3**: create_regression_model
- **level_6**: SimpleAverageEnsemble
- **level_7**: build_success_result, create_ensembling_method

## Usage Example

```python
from level_8 import run_regression_cv_fold, create_regression_ensemble_from_paths

# Run a single CV fold
score = run_regression_cv_fold(
    fold=0, n_folds=5,
    all_features=X, all_targets=y, fold_assignments=fold_assignments,
    regression_model_type="ridge", hyperparameters={}, config=config,
    metric_calculator=metric_calculator,
)

# Create ensemble from paths
ensemble = create_regression_ensemble_from_paths(
    model_paths=["path1", "path2"],
    model_configs=[{"feature_filename": "emb"}, {"feature_filename": "emb"}],
    method="weighted_average",
    cv_scores=[0.85, 0.82],
)
predictions = ensemble.predict(features)
```
