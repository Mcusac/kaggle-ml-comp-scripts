# level_6.tabular

## Purpose

Tabular model trainer, predictor, and MLP model implementation.

## Contents

- `tabular_trainer.py` — TabularTrainer
- `tabular_predictor.py` — TabularPredictor
- `mlp_model.py` — MLPModel (PyTorch-based multi-label classifier)

## Public API

| Name | Description |
|------|-------------|
| `TabularTrainer` | Trainer for tabular models |
| `TabularPredictor` | Predictor for tabular models |
| `MLPModel` | Multi-layer perceptron for tabular data |

## Dependencies

- **level_0**: get_logger, get_torch
- **level_1**: TabularDataset, get_device
- **level_2**: get_train_test_split, run_train_epoch, run_validate_epoch, validate_array
- **level_5**: BaseTabularModel, SparseTabularDataset, calculate_metrics

## Usage Example

```python
from layers.layer_0_core.level_6 import TabularTrainer, TabularPredictor, MLPModel, LogisticRegressionModel

model = LogisticRegressionModel(random_state=42)
trainer = TabularTrainer(model, validation_split=0.2)
trainer.fit(X_train, y_train)

predictor = TabularPredictor(model, threshold=0.5)
preds = predictor.predict(X_test)
```
