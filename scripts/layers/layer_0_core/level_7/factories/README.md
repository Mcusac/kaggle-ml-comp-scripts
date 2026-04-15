# level_7.factories

## Purpose

Factory functions that create tabular models and ensembling methods by name.

## Contents

| Module | Description |
|--------|-------------|
| `tabular_model_factory.py` | Create tabular model by type (logistic, ridge, xgboost, lgbm, mlp) |
| `create_ensembling_method.py` | Create ensembling method by name |

## Public API

| Name | Description |
|------|-------------|
| `create_tabular_model` | Create tabular model instance by type |
| `create_ensembling_method` | Create ensembling method by name |

## Dependencies

- **level_0**: EnsemblingMethod
- **level_3**: PerTargetWeightedEnsemble
- **level_5**: BaseTabularModel
- **level_6**: Tabular models (MLP, LogisticRegression, Ridge, XGBoost, LightGBM), ensembling methods

## Usage Example

```python
from layers.layer_0_core.level_7 import create_tabular_model, create_ensembling_method

# Create tabular model
model = create_tabular_model("ridge", input_dim=100, output_dim=1)

# Create ensembling method
ensemble = create_ensembling_method("weighted_average")
```
