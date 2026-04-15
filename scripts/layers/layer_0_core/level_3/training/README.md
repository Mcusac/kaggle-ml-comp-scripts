# level_3 training

## Purpose

Training components: a timm vision model wrapper, OOM-retry execution engine, TTA predictor, and tabular sklearn regression model wrappers.

## Contents

- `timm_model.py` — `TimmModel`: wraps any timm backbone with a configurable regression head; supports single-image and split-image (cross-gated) forward modes.
- `tta_predictor.py` — `TTAPredictor`: applies a list of TTA transforms to each batch and averages predictions for improved robustness.
- `oom_retry.py` — `handle_oom_error_with_retry`: generic CUDA OOM retry engine that halves batch size on each attempt.
- `sklearn_models.py` — concrete `BaseMultiOutputRegressionModel` subclasses for HistGradientBoosting, GradientBoosting, CatBoost, LGBM, XGBoost, and Ridge; `create_regression_model` factory function.

## Public API

- `TimmModel` — timm-backed vision model with `forward`, `freeze_backbone`, `unfreeze_backbone`, `get_input_size`, `is_pretrained` methods.
- `TTAPredictor` — TTA inference class with `predict` (batch DataLoader) and `predict_single_image` methods.
- `handle_oom_error_with_retry(func, *args, batch_size_key, initial_batch_size, ...)` — execute a function with automatic batch size reduction on CUDA OOM.
- `HistGradientBoostingRegressorModel`, `GradientBoostingRegressorModel`, `CatBoostRegressorModel`, `LGBMRegressorModel`, `XGBoostRegressorModel`, `RidgeRegressorModel` — sklearn multi-output regression model wrappers.
- `create_regression_model(model_type, **params)` — factory returning a regression model by string type key.

## Dependencies

- **level_0** — `get_logger`, `get_torch`.
- **level_1** — `BaseVisionModel` (base class for `TimmModel`), `forward_with_amp`.
- **level_2** — `TimmWeightLoader` (pretrained weight loading), `build_tta_transforms`, `TTAVariant`, `is_oom_error`, `recover_from_oom`, `BaseMultiOutputRegressionModel` (base class for sklearn wrappers), `get_gradient_boosting_regressor`, `get_catboost`, `get_lightgbm`, `get_xgboost`, `get_ridge`.

## Usage Example

```python
from layers.layer_0_core.level_3.training import TimmModel, create_regression_model, handle_oom_error_with_retry

model = TimmModel(model_name="efficientnet_b2", num_classes=6, dataset_type="single")
model.freeze_backbone()

lgbm = create_regression_model("lgbm", n_estimators=500)
lgbm.fit(X_train, y_train)

result = handle_oom_error_with_retry(
    train_one_epoch,
    model,
    loader,
    batch_size_key="batch_size",
    initial_batch_size=32,
)
```
