# infra/level_4/trainer — Trainer factory

**On disk:** `…/level_0_infra/level_4/trainer/`. **Import:** `layers.layer_1_competition.level_0_infra.level_4` (prefer the tier barrel).

## Purpose

Creates the appropriate trainer instance based on config mode: `FeatureExtractionTrainer` when `config.model.feature_extraction_mode` is True, otherwise `BaseModelTrainer`.

## Contents

| Module | Description |
|---|---|
| `factory` | `create_trainer` — inspects config and instantiates the correct trainer. |

## Public API

| Name | Description |
|---|---|
| `create_trainer` | Creates a trainer instance appropriate for the given config and device. |

## Dependencies

| Source | Reason |
|---|---|
| `layers.layer_0_core.level_0` | `get_config_value`, `get_logger`. |
| `layers.layer_0_core.level_5` | `BaseModelTrainer`. |
| `layers.layer_1_competition.level_0_infra.level_3` | `FeatureExtractionTrainer` (re-exported at infra `level_3` barrel). |

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_4 import create_trainer

trainer = create_trainer(
    config=config,
    device=device,
    model=None,
    metric_calculator=metric_calculator,
)
trainer.train(train_loader, val_loader, num_epochs=10, save_dir=save_dir)
```
