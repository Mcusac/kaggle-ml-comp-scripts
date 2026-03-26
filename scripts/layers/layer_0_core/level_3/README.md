# level_3

## Purpose

Composed pipelines and higher-level components for ML competition workflows: dataloaders, feature extraction, metrics, ensemble methods, training models, and orchestration.

**Dependency and import policy:** `level_3` may import only from **level_0**, **level_1**, and **level_2** (lower levels). Imports of other modules under `level_3` must use fully qualified names (`from level_3.subpackage.module import ...`) so dependencies are explicit. In `__init__.py` only, `from . import submodule` is allowed when a fully qualified same-package import would be circular during package initialization.

## Contents

- `dataloader/` — PyTorch DataLoader factories for training and validation splits with configurable augmentation presets.
- `ensemble/` — Prediction blending, learned weight fitting, meta-model factory, and per-target weighted ensembling.
- `transforms/` — Config-driven transform factory: build_train_transform, build_val_transform, build_tta_transforms.
- `features/` — SigLIP patch embedding extractor, supervised dimensionality-reduction engine (PCA + PLS + GMM), handcrafted protein feature extraction (sequential, parallel, streaming), and DataLoader-based bulk extraction.
- `metrics/` — Classification and regression metric functions and `Metric` subclasses; auto-registers all standard metrics into the global registry on import.
- `runtime/` — Path and image-path validation utilities.
- `training/` — timm vision model wrapper, TTA predictor, OOM-retry engine, and tabular sklearn regression model wrappers.
- `workflows/` — Train-then-test CV pipeline orchestration and tqdm progress bar formatter.

## Public API

All names from each sub-package's `__all__` are re-exported at this level. See each sub-package's `README.md` for the full listing.

Key exports by sub-package:
- **dataloader**: `create_train_dataloader`, `create_val_dataloader`, `build_transforms_for_dataloaders`
- **ensemble**: `blend_predictions`, `learn_blending_weights`, `create_meta_model`, `PerTargetWeightedEnsemble`
- **features**: `SigLIPExtractor`, `SupervisedEmbeddingEngine`, `extract_all_features`, `extract_handcrafted_features_for_ids`, `extract_handcrafted_parallel`, `stream_features`
- **metrics**: `calculate_accuracy`, `calculate_rmse`, `calculate_regression_metrics`, `calculate_classification_metrics`, `RMSEMetric`, `AccuracyMetric`, and all other metric classes
- **runtime**: `validate_file_exists`, `validate_path_is_file`, `validate_image_path`, `validate_image_paths_in_dataframe`
- **transforms**: `build_train_transform`, `build_val_transform`, `build_tta_transforms`
- **training**: `TimmModel`, `TTAPredictor`, `handle_oom_error_with_retry`, `create_regression_model`, and all regression model classes
- **workflows**: `train_test_pipeline`, `ProgressFormatter`

## Dependencies

- **level_0** — Core abstractions, logging, errors, paths, vision, prediction utilities, runtime helpers.
- **level_1** — Dataset classes, feature extractor base, siglip class loaders, training helpers, registry, progress types.
- **level_2** — Transform builders, feature cache I/O, ensemble strategies, model lazy loaders, validation, training utilities.

## Usage Example

```python
from level_3 import (
    create_train_dataloader,
    TimmModel,
    TTAPredictor,
    calculate_regression_metrics,
    PerTargetWeightedEnsemble,
)

model = TimmModel(model_name="efficientnet_b2", num_classes=6)
train_loader = create_train_dataloader(train_df, "/data", cfg, (224, 224))
metrics = calculate_regression_metrics(y_true, y_pred)
```
