# infra/level_4/trainer — Trainer factory

**On disk:** `…/level_0_infra/level_4/trainer/`. **Import:** `layers.layer_1_competition.level_0_infra.level_4`.

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
| Level | Reason |
|---|---|
| `level_0` | `get_config_value`, `get_logger`. |
| `level_5` | `BaseModelTrainer`. |
| `layers.layer_1_competition.level_0_infra.level_0` | `get_feature_extraction_mode`. |
| `layers.layer_1_competition.level_0_infra.level_2` | `FeatureExtractionTrainer`. |

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
