# infra/level_2/feature_extraction — Training and test-time feature extraction

**On disk:** `…/level_0_infra/level_2/feature_extraction/`. **Import:** `layers.layer_1_competition.level_0_infra.level_2`.

## Purpose

Two-stage feature extraction training and test-time feature extraction for stacking and ensemble pipelines.

## Contents

| Module | Description |
|--------|-------------|
| `helpers` | FeatureExtractionConfigHelper, FeatureExtractionHelper — config extraction and joint feature+target extraction |
| `trainer` | FeatureExtractionTrainer — extract features, train regression model |
| `test_extractor` | extract_test_features_from_model, find_feature_filename_from_ensemble_metadata |

## Public API

- **FeatureExtractionConfigHelper** — validate_inputs, extract_dataset_type, extract_regression_model_type, extract_feature_extraction_model_name
- **FeatureExtractionHelper** — extract_all_features(loader) → (features, targets)
- **FeatureExtractionTrainer** — extract_all_features, train
- **extract_test_features_from_model** — Create model, dataloader, extract features, cleanup GPU
- **find_feature_filename_from_ensemble_metadata** — Resolve feature_filename from ensemble model_metadata.json

## Dependencies

- **level_0:** get_logger, get_torch, ensure_dir (`trainer`)
- **level_1:** split_features_by_fold (`trainer`); cleanup_gpu_memory, get_device (`test_extractor`)
- **level_2:** FeatureExtractor
- **level_3:** create_regression_model (`trainer`)
- **level_5:** save_regression_model (`trainer`)
- **level_6:** create_test_dataloader (`test_extractor`)
- **layers.layer_1_competition.level_0_infra.level_0:** get_dataset_type, get_feature_extraction_model_name, get_regression_model_type (`helpers`)
- **layers.layer_1_competition.level_0_infra.level_1:** create_feature_extraction_model, validate_feature_extraction_inputs

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_2.feature_extraction import (
    FeatureExtractionTrainer,
    extract_test_features_from_model,
)

trainer = FeatureExtractionTrainer(config, device, metric_calculator=metric)
history = trainer.train(train_loader, val_loader, save_dir=path)

features = extract_test_features_from_model(
    test_csv_path=path,
    data_root=data_root,
    dataset_type="split",
    config=config,
    data_schema=data_schema,
)
```
