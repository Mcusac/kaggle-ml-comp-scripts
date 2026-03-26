# RNA3D `level_2.orchestration`

## Purpose

Implements tier-2 workflows: trainer registration, submission generation, and validation-driven tuning for RNA3D models (currently centered on `baseline_approx`).

## Contents

- **`trainer_registry.py`** — Maps model names to trainer callables and implements `baseline_approx` training (template bank pickle).
- **`submission.py`** — `submit_pipeline` with `single`, `ensemble`, and `stacking` strategies using shared ensembling utilities from `level_0`.
- **`tuning.py`** — `tune_pipeline` grid search over `BaselineApproxConfig` with TM-score on validation; writes `best_config.json` under contest output paths.

## Public API

Re-exported by `level_2/__init__.py` (consumers should import from `layers.layer_1_competition.level_1_impl.level_rna3d.level_2`):

| Name | Description |
|------|-------------|
| `get_trainer` | Returns the trainer callable for a registered model name, or `None`. |
| `list_available_models` | Sorted list of registered model names. |
| `submit_pipeline` | Builds a competition submission CSV from the chosen strategy and models. |
| `tune_pipeline` | Grid-searches hyperparameters on validation data; returns the best config dict. |

## Dependencies

- **`level_0`** — `get_logger`, `ensure_dir`, `combine_predictions_weighted_average`, `fit_stacking_weights_from_scores`.
- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_0`** — `validate_rna3d_inputs`, `RNA3DPaths`.
- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_1`** — `BaselineApproxConfig`, `evaluate_predictions_tm`, prediction and CSV helpers, template construction for training.

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_rna3d.level_2 import submit_pipeline, tune_pipeline

best = tune_pipeline(
    data_root="/path/to/data",
    model_name="baseline_approx",
    search_type="quick",
)
out = submit_pipeline(
    data_root="/path/to/data",
    strategy="single",
    models=["baseline_approx"],
)
print(best["_tune_score"], out)
```
