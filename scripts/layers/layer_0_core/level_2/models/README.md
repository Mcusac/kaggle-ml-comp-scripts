# models

Model wrappers and lazy-loaded ML library imports.

## Purpose

Provides concrete model implementations (DINOv2, sklearn/boosting), a regression base class for multi-output models, and a Timm weight loader for offline environments.

## Contents

- `dinov2_model.py` — `DINOv2Model`: HuggingFace DINOv2 with FiLM/cross-gating fusion and regression head
- `regression_base.py` — `BaseMultiOutputRegressionModel`: sklearn-compatible base for multi-output regression
- `sklearn_imports.py` — Lazy-loaded factory functions for sklearn, catboost, lightgbm, and xgboost classes
- `timm_loader.py` — `TimmWeightLoader`: resolves and loads Timm model weights in offline/Kaggle environments

## Public API

- `DINOv2Model` — DINOv2 backbone with configurable fusion and regression head; loads via HuggingFace
- `BaseMultiOutputRegressionModel` — Abstract base for sklearn-style multi-output regressors with array validation
- `TimmWeightLoader` — Resolves Timm pretrained weight paths for offline environments
- Lazy import factories (each returns the class when called):
  - `get_standard_scaler()`, `get_pca()`, `get_pls_regression()`, `get_gaussian_mixture()`
  - `get_gradient_boosting_regressor()`, `get_hist_gradient_boosting_regressor()`, `get_random_forest_regressor()`
  - `get_catboost()`, `get_lightgbm()`, `get_lgbm_classifier()`, `get_xgboost()`, `get_xgb_classifier()`
  - `get_ridge()`, `get_logistic_regression()`, `get_ridge_classifier()`, `get_linear_regression()`, `get_lasso()`, `get_elastic_net()`
  - `get_kfold()`, `get_stratified_kfold()`, `get_train_test_split()`, `get_cross_val_score()`

## Dependencies

- **level_0** — `get_logger`, `get_torch`
- **level_1** — `FiLM`, `BaseVisionModel`, `lazy_import`, `check_array_finite`, `configure_huggingface_cache`, `resolve_offline_weight_cache`

## Usage Example

```python
from layers.layer_0_core.level_2.models import DINOv2Model, get_ridge

model = DINOv2Model(model_name="facebook/dinov2-base", num_classes=6)
Ridge = get_ridge()
regressor = Ridge(alpha=1.0)
```
