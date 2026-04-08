# level_8.regression

## Purpose

Regression head support for grid search and inference: run a single CV fold on pre-extracted features, build variant result dicts, and ensemble multiple saved regression models.

## Contents

| Module | Description |
|--------|-------------|
| `regression_variants.py` | `run_regression_cv_fold`, `create_regression_variant_result` |
| `regression_ensemble.py` | `RegressionEnsemble`, `create_regression_ensemble_from_paths` |

## Public API

| Name | Description |
|------|-------------|
| `run_regression_cv_fold` | One CV fold for a regression model |
| `create_regression_variant_result` | Build result dict for a regression variant |
| `RegressionEnsemble` | Combine predictions from loaded models |
| `create_regression_ensemble_from_paths` | Factory from paths and metadata |

## Dependencies

- **level_0**: Logging, `EnsemblingMethod`
- **level_1**: `split_features_by_fold`
- **level_3**: `create_regression_model`
- **level_4**: `load_pickle`
- **level_6**: `SimpleAverageEnsemble`
- **level_7**: `build_success_result`, `create_ensembling_method`

## Usage Example

```python
from level_8 import run_regression_cv_fold, create_regression_ensemble_from_paths

score = run_regression_cv_fold(
    fold=0,
    n_folds=5,
    all_features=X,
    all_targets=y,
    fold_assignments=fold_assignments,
    regression_model_type="ridge",
    hyperparameters={},
    config=config,
    metric_calculator=metric_calculator,
)

ensemble = create_regression_ensemble_from_paths(
    model_paths=["path1", "path2"],
    model_configs=[{"feature_filename": "emb"}, {"feature_filename": "emb"}],
    method="weighted_average",
    cv_scores=[0.85, 0.82],
)
predictions = ensemble.predict(features)
```
