# infra/level_2/feature_extraction

**On disk:** `…/level_0_infra/level_2/feature_extraction/`.  
**Import:** prefer `layers.layer_1_competition.level_0_infra.level_2` (package barrel).

## Purpose

Helper types and functions for feature extraction during training and inference: joint feature/target batches from a loader, test-set feature matrices for stacking, and resolving cached feature filenames from ensemble export metadata.

## Contents

| Module | Description |
|--------|-------------|
| `feature_extraction_helper.py` | `FeatureExtractionHelper` — wraps core `FeatureExtractor` for joint feature+target extraction. |
| `test_extractor.py` | `extract_test_features_from_model`, `find_feature_filename_from_ensemble_metadata`. |

## Public API

(Same symbols as `feature_extraction/__init__.py`.)

- **FeatureExtractionHelper** — `extract_all_features(loader) -> (features, targets)`.
- **extract_test_features_from_model** — End-to-end test features using infra `create_feature_extraction_model` and core dataloading.
- **find_feature_filename_from_ensemble_metadata** — Walk ensemble `model_paths` and read `feature_filename` from `model_metadata.json`.

## Dependencies

- **`layers.layer_0_core`:** `FeatureExtractor`, `get_logger`, `get_device`, `cleanup_gpu_memory`, `create_streaming_test_dataloader`, `load_json`.
- **`layers.layer_1_competition.level_0_infra.level_1`:** `create_feature_extraction_model`.

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_2 import (
    FeatureExtractionHelper,
    extract_test_features_from_model,
)

from layers.layer_0_core.level_2 import FeatureExtractor

helper = FeatureExtractionHelper(feature_extractor, dataset_type="split")
X, y = helper.extract_all_features(train_loader)

test_X = extract_test_features_from_model(
    test_csv_path=csv_path,
    data_root=data_root,
    dataset_type="split",
    config=config,
    data_schema=data_schema,
)
```
