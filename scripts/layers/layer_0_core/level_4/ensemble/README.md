# level_4.ensemble

## Purpose

Stacking ensemble that trains a meta-model on base model validation predictions. Learns per-target combination weights.

## Contents

| Module | Description |
|--------|-------------|
| meta_model_stacking | stacking_ensemble_with_validation |

## Public API

| Export | Description |
|--------|-------------|
| stacking_ensemble_with_validation | Stack base models with learned meta-model (ridge/linear/lasso) |

## Dependencies

- **level_0** — get_logger, DataValidationError, validate_targets
- **level_1** — validate_paired_predictions
- **level_3** — create_meta_model

## Usage Example

```python
from layers.layer_0_core.level_4 import stacking_ensemble_with_validation

ensemble_preds = stacking_ensemble_with_validation(
    base_predictions_train=[pred_train_1, pred_train_2],
    base_predictions_val=[pred_val_1, pred_val_2],
    y_val=y_val,
    meta_model_type="ridge",
)
```
