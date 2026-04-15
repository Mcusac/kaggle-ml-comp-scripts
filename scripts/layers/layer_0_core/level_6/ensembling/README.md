# level_6.ensembling

## Purpose

Averaging-based EnsemblingMethod implementations that wrap the functional averaging API in the EnsemblingMethod contract.

## Contents

- `ensembling_methods.py` — SimpleAverageEnsemble, WeightedAverageEnsemble, RankedAverageEnsemble, PercentileAverageEnsemble, TargetSpecificEnsemble

## Public API

| Name | Description |
|------|-------------|
| `SimpleAverageEnsemble` | Equal-weight ensemble |
| `WeightedAverageEnsemble` | Score-proportional ensemble |
| `RankedAverageEnsemble` | Model-rank-weighted ensemble |
| `PercentileAverageEnsemble` | Percentile-weighted ensemble |
| `TargetSpecificEnsemble` | Per-target model selection |

## Dependencies

- **level_0**: EnsemblingMethod, get_logger, calculate_percentile_weights
- **level_1**: validate_predictions_for_ensemble
- **level_2**: simple_average, model_rank_weights
- **level_5**: combine_with_fallback

## Usage Example

```python
from layers.layer_0_core.level_6 import WeightedAverageEnsemble

ensemble = WeightedAverageEnsemble()
combined = ensemble.combine(predictions_list, weights=cv_scores)
```
