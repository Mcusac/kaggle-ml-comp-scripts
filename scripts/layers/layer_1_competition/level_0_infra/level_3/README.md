---
generated: 2026-04-08
---

# infra/level_3 — Feature-extraction trainer

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_3/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_3`.

## Purpose

Exposes `FeatureExtractionTrainer` for two-stage contest pipelines (feature extraction plus regression on extracted features). Trainer *selection* (`create_trainer`) lives in infra **level_4**; contest grid search base types live in infra **level_1** (`ContestGridSearchBase`, `build_grid_search_context`).

## Contents

| Sub-package | Description |
|-------------|-------------|
| `trainer/` | `FeatureExtractionTrainer` implementation (`trainer/feature_extraction.py`). |

## Public API

| Name | Description |
|------|-------------|
| `FeatureExtractionTrainer` | Two-stage trainer: extract features, fit regression head, optional save via `save_regression_model`. |

## Dependencies

| Level | Reason |
|-------|--------|
| `layers.layer_0_core.level_0` | `ensure_dir`, `get_config_value`, `get_logger`, `get_torch`. |
| `layers.layer_0_core.level_1` | `split_features_by_fold`; validation guard. |
| `layers.layer_0_core.level_2` | `FeatureExtractor`, `get_required_config_value`. |
| `layers.layer_0_core.level_3` | `create_regression_model`. |
| `layers.layer_0_core.level_5` | `save_regression_model`. |
| `infra level_1` | `create_feature_extraction_model`. |
| `infra level_2` | `FeatureExtractionHelper`. |

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_3 import FeatureExtractionTrainer

# Typical construction matches level_4.create_trainer wiring for feature-extraction mode.
trainer = FeatureExtractionTrainer(
    config=config,
    device=device,
    metric_calculator=metric_calculator,
)

# Config-driven factory (end-to-end vs feature extraction):
from layers.layer_1_competition.level_0_infra.level_4 import create_trainer

trainer = create_trainer(config=config, device=device, metric_calculator=metric_calculator)
trainer.train(train_loader, val_loader, num_epochs=10, save_dir=save_dir)
```

## Related imports

- Grid search: `from layers.layer_1_competition.level_0_infra.level_1 import ContestGridSearchBase, build_grid_search_context`
