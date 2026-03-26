# level_3 ensemble

## Purpose

Higher-level ensemble combiners and meta-model factories that operate on lists of prediction arrays.

## Contents

- `blending_ensemble.py` — `blend_predictions` for combining prediction arrays via weighted average, geometric mean, or power mean; `learn_blending_weights` for fitting blend weights from a held-out validation set.
- `create_meta_model.py` — `create_meta_model` factory for instantiating ridge, linear, or lasso stacking meta-models.
- `per_target_weighted.py` — `PerTargetWeightedEnsemble` class that applies different weights per target column, dispatching to vectorized or loop-based kernels from level_0.

## Public API

- `blend_predictions(predictions_list, weights, method, power, padding_strategy)` — combine prediction arrays; pads shape mismatches automatically.
- `learn_blending_weights(predictions_list, y_val, method, alpha)` — learn per-model blend weights from validation data using ridge, linear, or L-BFGS-B optimisation.
- `create_meta_model(meta_model_type, meta_model_params, random_state)` — instantiate a stacking meta-model ('ridge', 'linear', or 'lasso').
- `PerTargetWeightedEnsemble` — `EnsemblingMethod` subclass; combine multi-target predictions with per-target weight dicts.

## Dependencies

- **level_0** — `EnsemblingMethod` (base class), `get_logger`, `validate_predictions_list`, `get_shape_and_targets`, `combine_predictions_loop`, `combine_predictions_vectorized`.
- **level_2** — `build_weight_matrix` for weight matrix construction; `get_ridge`, `get_linear_regression`, `get_lasso`, `weighted_average`, `geometric_mean`, `power_average` for blend strategies.

## Usage Example

```python
from level_3.ensemble import blend_predictions, learn_blending_weights, PerTargetWeightedEnsemble

weights = learn_blending_weights(val_predictions, y_val, method="ridge")
combined = blend_predictions(test_predictions, weights=weights, method="weighted_average")

ensemble = PerTargetWeightedEnsemble(
    per_target_weights={"target_0": [0.6, 0.4], "target_1": [0.3, 0.7]},
    target_names=["target_0", "target_1"],
)
result = ensemble.combine(test_predictions)
```
