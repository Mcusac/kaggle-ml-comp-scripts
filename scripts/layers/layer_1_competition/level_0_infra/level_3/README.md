# infra/level_3 — Trainer factory and contest grid search

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_3/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_3`.

## Purpose

Provides trainer creation and contest grid search orchestration. Selects the appropriate trainer (end-to-end vs feature-extraction) from config, and supplies contest-aware grid search base and context builder.

## Contents
| Sub-package | Description |
|---|---|
| `trainer/` | Factory that inspects `config.model.feature_extraction_mode` and returns `BaseModelTrainer` or `FeatureExtractionTrainer`. |
| `grid_search/` | Contest-aware grid search base class and context builder for orchestration. |

## Public API
| Name | Description |
|---|---|
| `create_trainer` | Creates a trainer instance appropriate for the given config and device. |
| `ContestGridSearchBase` | Contest-aware grid search base that injects contest paths and config. |
| `build_grid_search_context` | Builds a context object with contest paths, config, and injected overrides. |

## Dependencies
| Level | Reason |
|---|---|
| `level_0` | `get_logger`, `get_config_value` for logging and config extraction. |
| `level_5` | `BaseModelTrainer` — end-to-end training. |
| `level_6` | `GridSearchBase` — framework grid search infrastructure. |
| `infra level_0` | `get_contest`, `get_feature_extraction_mode` — contest registry and config helpers. |
| `infra level_2` | `FeatureExtractionTrainer` — two-stage feature-extraction training. |

## Usage Example
```python
from layers.layer_1_competition.level_0_infra.level_3 import create_trainer, ContestGridSearchBase, build_grid_search_context

# Trainer creation
trainer = create_trainer(
    config=config,
    device=device,
    model=None,
    metric_calculator=metric_calculator,
)
trainer.train(train_loader, val_loader, num_epochs=10, save_dir=save_dir)

# Grid search context
ctx = build_grid_search_context("csiro", metric_calculator=calc_fn)
paths = ctx.get_paths()
config = ctx.get_config()

# Grid search base (subclass in contest layer)
class MyGridSearch(ContestGridSearchBase):
    def _generate_variant_grid(self): ...
    def _run_variant(self, variant, idx): ...
    def _create_variant_key(self, variant): ...
```
