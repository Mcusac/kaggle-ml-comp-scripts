---
generated: 2026-04-08
---

# infra/level_3/trainer — `FeatureExtractionTrainer`

**On disk:** `…/level_0_infra/level_3/trainer/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_3` (barrel) or `…level_3.trainer` for cycle breaks only.

## Purpose

Implements `FeatureExtractionTrainer` for two-stage training. For a config-driven choice between this trainer and end-to-end `BaseModelTrainer`, use **`layers.layer_1_competition.level_0_infra.level_4.create_trainer`** (not this tier’s barrel).

## Contents

| Module | Description |
|--------|-------------|
| `feature_extraction.py` | `FeatureExtractionTrainer` class. |

## Public API

| Name | Description |
|------|-------------|
| `FeatureExtractionTrainer` | Two-stage trainer (feature extractor + regression model). |

## Dependencies

Same as parent `level_3` README (core levels 0–5, infra `level_1` / `level_2`).

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_3 import FeatureExtractionTrainer

trainer = FeatureExtractionTrainer(
    config=config,
    device=device,
    metric_calculator=metric_calculator,
)
```

Config-based factory:

```python
from layers.layer_1_competition.level_0_infra.level_4 import create_trainer

trainer = create_trainer(
    config=config,
    device=device,
    metric_calculator=metric_calculator,
)
```
