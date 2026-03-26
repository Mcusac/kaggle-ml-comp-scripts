# infra/level_2 — Feature-extraction trainer and regression submission

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_2/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_2`.

## Purpose

Two-stage training (feature extraction + regression) and submission creation for contest pipelines. Extracts features from images, trains regression models (LGBM/XGB/Ridge), and produces submission CSVs.

## Contents

| Sub-package | Description |
|-------------|-------------|
| `feature_extraction/` | Trainer, config helpers, and test-time feature extraction |
| `submission/` | Expand predictions to submission format, save CSV, create regression submission |

## Public API

All names exported from `__init__.py`:

- **FeatureExtractionConfigHelper** — Static config extraction (dataset_type, regression_model_type, feature_extraction_model_name)
- **FeatureExtractionHelper** — Wraps FeatureExtractor for joint feature+target extraction from DataLoader
- **FeatureExtractionTrainer** — Two-stage trainer: extract features, train regression model
- **create_regression_submission** — Load regression model, extract test features, predict, expand, save
- **expand_predictions_to_submission_format** — Expand primary predictions to all targets, apply post-processing
- **save_submission** — Save submission DataFrame to CSV (Kaggle-aware)
- **extract_test_features_from_model** — Extract test features using feature extraction model
- **find_feature_filename_from_ensemble_metadata** — Resolve feature_filename from ensemble model metadata

## Dependencies

- **level_0:** ensure_dir, get_logger, get_torch
- **level_1:** split_features_by_fold, resolve_environment_path, cleanup_gpu_memory, get_device
- **level_2:** FeatureExtractor
- **level_3:** create_regression_model
- **level_4:** load_json
- **level_5:** save_regression_model, load_and_validate_test_data
- **level_6:** create_test_dataloader
- **layers.layer_1_competition.level_0_infra.level_0:** get_dataset_type, get_feature_extraction_model_name, get_regression_model_type (package root)
- **layers.layer_1_competition.level_0_infra.level_1:** create_feature_extraction_model, validate_feature_extraction_inputs

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_2 import FeatureExtractionTrainer, create_regression_submission

# Two-stage training
trainer = FeatureExtractionTrainer(
    config=config,
    device=device,
    metric_calculator=contest_metric,
    num_primary_targets=config.num_primary_targets,
)
history = trainer.train(
    train_loader=train_loader,
    val_loader=val_loader,
    save_dir=fold_dir,
)

# Create submission from trained regression model
create_regression_submission(
    regression_model_path=str(model_path),
    feature_extraction_model_name="dinov2_base",
    test_csv_path=str(test_csv_path),
    data_root=data_root,
    config=config,
    device=device,
    output_path=str(output_path),
    data_schema=data_schema,
    post_processor=post_processor,
)
```
