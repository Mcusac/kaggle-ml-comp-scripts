# Level 2: Component Implementations

Concrete component implementations built on level_0 and level_1. Does not depend on level_3 or higher.

## Purpose

Provides ready-to-use ML pipeline components: model wrappers, data loaders, feature extractors, ensemble strategies, training loops, validation utilities, vision transforms, and grid search tooling.

## Contents

| Subpackage | Responsibility |
|---|---|
| `analysis` | Cross-validation analysis and fold score diagnostics |
| `dataloader` | Dataset factory and worker seeding for DataLoaders |
| `ensemble_strategies` | Prediction averaging, weighting, and stacking result handlers |
| `feature_extractors` | Backbone feature extraction, protein features, semantic scoring |
| `grid_search` | Environment setup, parameter grid resolution, variant accumulation |
| `inference` | Vision model batch inference |
| `models` | DINOv2, Timm, and sklearn/boosting lazy-loaded model wrappers |
| `progress` | Progress bar manager and timing/throughput metrics |
| `runtime` | Orchestration-level hardware environment detection |
| `training` | Training and validation executors, epoch runners, checkpointing |
| `validation` | Input validators for arrays, dataframes, lists, and series |
| `vision_transforms` | Preprocessing pipelines, TTA, image cleaning, augmentation presets |

## Public API

See each subpackage's `README.md` for detailed exports.

Key top-level exports (re-exported from subpackages):
- `DINOv2Model`, `BaseMultiOutputRegressionModel`, `TimmWeightLoader` — model wrappers
- `FeatureExtractor`, `SemanticFeatureExtractor`, `extract_handcrafted_features` — feature extraction
- `build_preprocessing_transforms`, `build_tta_transforms`, `TTAVariant` — vision transforms
- `run_train_epoch`, `run_validate_epoch`, `TrainingPhaseExecutor`, `ValidationPhaseExecutor` — training
- `simple_average`, `weighted_average`, `build_weight_matrix`, `log_pipeline_completion` — ensemble strategies and pipeline logging
- `ProgressBarManager`, `ProgressMetrics` — progress tracking

## Dependencies

- **level_0** — logging, errors, config, paths, device utilities, scoring primitives
- **level_1** — validation guards, training utilities, data processing, feature base classes, runtime config

## Usage Example

```python
from level_1 import ProgressConfig
from level_2 import ProgressBarManager, ProgressMetrics

config = ProgressConfig()
metrics = ProgressMetrics(config)
manager = ProgressBarManager(verbosity=config.verbosity)
bar_id = manager.create_bar("train", total=100, desc="Training", level=1)
metrics.register_bar(bar_id)
# ... training loop
manager.close_all()
```
