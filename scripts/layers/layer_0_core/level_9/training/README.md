# level_9.training

## Purpose

Workflows that compose level_8 training with evaluation, cross-validation, or export: cross-validation over folds and train-then-export for submission.

## Contents

| Module | Description |
|--------|-------------|
| `cross_validate.py` | `CrossValidateWorkflow` — vision or tabular k-fold CV using `TrainPipeline` and scoring |
| `train_and_export.py` | `TrainAndExportWorkflow` — `TrainPipeline` then `ExportPipeline` |

## Public API

| Name | Description |
|------|-------------|
| `CrossValidateWorkflow` | Runs k-fold CV; vision uses holdout metrics from training; tabular runs predict + evaluate per fold |
| `TrainAndExportWorkflow` | Trains a model and exports it with metadata for downstream use |

## Dependencies

- **level_0**: `get_logger`
- **level_1**: `BasePipeline`
- **level_4**: `EvaluatePipeline` (CV tabular path)
- **level_6**: `PredictPipeline` (CV tabular path)
- **level_5**: `ExportPipeline` (train-and-export path)
- **level_8**: `TrainPipeline`

## Usage Example

```python
import path_bootstrap

path_bootstrap.prepend_framework_paths()

from layers.layer_0_core.level_9 import CrossValidateWorkflow

wf = CrossValidateWorkflow(
    config=config,
    model_type="tabular",
    n_folds=5,
    X=X,
    y=y,
)
wf.setup()
out = wf.execute()
```

## Generated

2026-04-08 (audit pass 1).
