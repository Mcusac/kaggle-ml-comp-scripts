# RNA3D `level_2`

## Purpose

Contest tier 2 orchestration for RNA3D: register trainable models, run hyperparameter search on validation data, and build submission CSVs from one or more models.

## Contents

- **`orchestration/`** — Implementation modules aggregated by `__init__.py`; see that package’s README for module-level detail.

## Public API

| Name | Description |
|------|-------------|
| `get_trainer` | Returns the trainer callable for a model name, or `None` if unregistered. |
| `list_available_models` | Sorted list of registered model names. |
| `submit_pipeline` | Writes a submission CSV using `single`, `ensemble`, or `stacking`. |
| `tune_pipeline` | Grid-searches `baseline_approx` on validation; returns best config dict. |

## Dependencies

- **`level_0`** — Logging, ensembling/stacking helpers (`combine_predictions_weighted_average`, `fit_stacking_weights_from_scores`), directory creation (`ensure_dir`).
- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_0`** — Input validation, TM-score evaluation, contest output paths.
- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_1`** — Baseline approximation config, training/prediction helpers, submission CSV formatting, template building for registered trainers.

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_rna3d.level_2 import (
    get_trainer,
    submit_pipeline,
    tune_pipeline,
)

tune_pipeline(
    data_root="/path/to/competition/data",
    model_name="baseline_approx",
    search_type="quick",
)

submit_pipeline(
    data_root="/path/to/competition/data",
    strategy="single",
    models=["baseline_approx"],
    output_csv="/path/to/submission.csv",
)

trainer = get_trainer("baseline_approx")
if trainer is not None:
    trainer("/path/to/competition/data", "/path/to/output_dir")
```
