# infra/level_4/fold_orchestration

**On disk:** `…/level_0_infra/level_4/fold_orchestration/`. **Import:** `layers.layer_1_competition.level_0_infra.level_4`.

## Purpose

Coordinates trainer creation, dataloader construction, training loop execution, and GPU cleanup for a single cross-validation fold.

## Contents

| Module | Description |
|--------|-------------|
| `single_fold` | `train_single_fold` — orchestrates trainer + dataloaders for one CV fold and returns the best validation score. |

## Public API

| Name | Description |
|------|-------------|
| `train_single_fold` | Runs training for a single fold and returns the best score achieved. |

## Dependencies

| Source | Reason |
|-------|--------|
| `layers.layer_0_core.level_0` | `ensure_dir` for fold output directory creation; `get_logger` for logging. |
| `layers.layer_0_core.level_1` | `get_device` for automatic device selection; `cleanup_gpu_memory` for post-fold cleanup. |
| `layers.layer_0_core.level_3` | `create_train_dataloader` and `create_val_dataloader` for dataset-aware loader construction. |
| `layers.layer_1_competition.level_0_infra.level_4` | `create_trainer` — package barrel (`level_4/__init__.py` imports `trainer` before `fold_orchestration`, so this resolves during submodule load). |
| `layers.layer_1_competition.level_0_infra.level_3` | `FeatureExtractionTrainer` — used when `create_trainer` selects feature-extraction mode. |

## Usage Example

```python
from pathlib import Path
from layers.layer_1_competition.level_0_infra.level_4 import train_single_fold

best_score = train_single_fold(
    fold=0,
    n_folds=5,
    train_data=train_df,
    val_data=val_df,
    data_root="/data/images",
    config=config,
    image_size=(224, 224),
    num_epochs=10,
    dataset_type="classification",
    model_dir=Path("models/run_001"),
    metric_calculator=None,
)
print(f"Fold 0 best score: {best_score:.4f}")
```
