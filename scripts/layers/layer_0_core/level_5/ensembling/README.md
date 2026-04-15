# ensembling

## Purpose

Prediction combination and stacking ensemble for regression and classification.

## Contents

- **combine.py**: apply_weighted_combination, combine_with_fallback
- **stacking_ensemble.py**: StackingEnsemble

## Public API

- `apply_weighted_combination(stacked, normalized_weights)` — Weighted sum of stacked predictions
- `combine_with_fallback(stacked, weights_array, predictions_list, ensemble_name)` — Combine with normalization, fallback to simple average if zero weights
- `StackingEnsemble` — OOF stacking with per-target Ridge meta-models

## Dependencies

- level_0: get_logger
- level_1: ensure_positive_weights, normalize_weights
- level_2: simple_average, get_ridge, get_kfold
- level_3: create_regression_model
- level_4: load_pickle

## Usage Example

```python
from layers.layer_0_core.level_5 import combine_with_fallback, StackingEnsemble
import numpy as np

combined = combine_with_fallback(
    stacked=np.stack(predictions),
    weights_array=weights,
    predictions_list=predictions,
    ensemble_name="weighted",
)

ensemble = StackingEnsemble(model_paths, model_configs, "siglip", n_folds=5)
oof, test = ensemble.generate_oof_predictions(X_train, y_train, X_test)
ensemble.fit_meta_models(oof, y_train)
final = ensemble.predict(test)
```
