# level_6.tabular_models

## Purpose

Tabular model implementations wrapping sklearn and boosting classifiers for multi-label classification.

## Contents

| Module | Description |
|--------|-------------|
| `linear.py` | LogisticRegressionModel, RidgeModel |
| `tree.py` | XGBoostModel, LightGBMModel |

## Public API

| Name | Description |
|------|-------------|
| `LogisticRegressionModel` | Logistic regression classifier |
| `RidgeModel` | Ridge classifier |
| `XGBoostModel` | XGBoost classifier |
| `LightGBMModel` | LightGBM classifier |

## Dependencies

- **level_0**: Logging
- **level_2**: get_logistic_regression, get_ridge_classifier, get_lgbm_classifier, get_xgb_classifier
- **level_5**: BaseTabularModel

## Usage Example

```python
from layers.layer_0_core.level_6 import LogisticRegressionModel, XGBoostModel

model = LogisticRegressionModel(random_state=42, max_iter=1000)
model.fit(X_train, y_train)
proba = model.predict_proba(X_test)
model.save("model.pkl")

loaded = LogisticRegressionModel()
loaded.load("model.pkl")
```
