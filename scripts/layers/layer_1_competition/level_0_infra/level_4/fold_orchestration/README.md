# infra/level_4/fold_orchestration

**On disk:** `…/level_0_infra/level_4/fold_orchestration/`. **Import:** `layers.layer_1_competition.level_0_infra.level_4`.

## Purpose

Coordinates trainer creation, dataloader construction, training loop execution, and GPU cleanup for a single cross-validation fold.

## Contents
| Module | Description |
|--------|-------------|
| `__init__.py` | Exports `train_single_fold` — orchestrates trainer + dataloaders for one CV fold and returns the best validation score. |

## Public API
| Name | Description |
|------|-------------|
| `train_single_fold` | Runs training for a single fold and returns the best score achieved. |

## Dependencies
| Level | Reason |
|-------|--------|
| `level_0` | `ensure_dir` for fold output directory creation; `get_logger` for logging. |
| `level_1` | `get_device` for automatic device selection; `cleanup_gpu_memory` for post-fold cleanup. |
| `level_3` | `create_train_dataloader` and `create_val_dataloader` for dataset-aware loader construction. |
| `infra level_3` | `create_trainer` for config-driven trainer instantiation. |

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
