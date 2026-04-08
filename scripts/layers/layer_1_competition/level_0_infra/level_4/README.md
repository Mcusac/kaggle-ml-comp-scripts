# infra/level_4 — Fold orchestration and trainer factory

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_4/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_4`.

## Purpose

Exposes config-driven trainer construction (`create_trainer`) and coordinates the full training pipeline for a single cross-validation fold (`train_single_fold`): device selection, trainer creation, dataloader construction, training loop execution, and GPU memory cleanup.

## Contents

| Sub-package / area | Description |
|---|---|
| `trainer/` | `create_trainer` — chooses `FeatureExtractionTrainer` vs `BaseModelTrainer` from config. |
| `fold_orchestration/` | `train_single_fold` — one CV fold end-to-end using infra trainers and core dataloaders. |

## Public API

| Name | Description |
|---|---|
| `create_trainer` | Builds the trainer instance implied by `config.model.feature_extraction_mode`. |
| `train_single_fold` | Runs training for a single fold and returns the best validation score. |

## Dependencies

| Source | Reason |
|---|---|
| `layers.layer_0_core.level_0` | `ensure_dir`, `get_logger` (fold output paths and logging). |
| `layers.layer_0_core.level_1` | `get_device`, `cleanup_gpu_memory`. |
| `layers.layer_0_core.level_3` | `create_train_dataloader`, `create_val_dataloader`. |
| `layers.layer_0_core.level_5` | `BaseModelTrainer` (factory default path). |
| `layers.layer_1_competition.level_0_infra.level_3` | `FeatureExtractionTrainer` when feature-extraction mode is enabled. |

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
