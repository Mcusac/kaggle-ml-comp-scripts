# Scoring

Percentile weight conversion and weighted prediction combination.

## Purpose

Converts raw model scores to percentile-based weights and combines weighted prediction arrays using both a reference loop implementation and a vectorized NumPy implementation.

## Contents

- `calculate_percentile_weights.py` – Convert scores to percentile ranks via `scipy.stats.rankdata`
- `combine_predictions.py` – Weighted combination of prediction arrays (loop and vectorized variants)
- `ensemble_weights.py` – Weighted average of prediction dicts, stacking weights from validation scores

## Public API

- `calculate_percentile_weights(scores)` – Return float32 array of percentile ranks (0–100) for each score
- `combine_predictions_loop(predictions_list, weight_matrix, result)` – Reference loop-based weighted sum
- `combine_predictions_vectorized(predictions_list, weight_matrix)` – Vectorized einsum-based weighted sum
- `combine_predictions_weighted_average(predictions_list, weights)` – Combine prediction dicts via weighted average
- `fit_stacking_weights_from_scores(scores, temperature)` – Fit stacking weights from validation scores (softmax-like)

## Dependencies

- numpy
- scipy (scipy.stats.rankdata)

## Usage Example

```python
import numpy as np
from level_0 import calculate_percentile_weights, combine_predictions_vectorized

scores = np.array([0.3, 0.9, 0.6])
weights = calculate_percentile_weights(scores)

predictions = [np.random.rand(10, 3), np.random.rand(10, 3)]
weight_matrix = np.ones((3, 2)) / 2.0
combined = combine_predictions_vectorized(predictions, weight_matrix)
```
