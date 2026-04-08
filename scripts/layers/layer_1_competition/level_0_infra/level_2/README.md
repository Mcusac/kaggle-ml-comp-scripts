# infra/level_2 — Feature extraction and CLI handler registry

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_2/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_2`.

## Purpose

Shared feature-extraction utilities for contest pipelines (joint feature/target extraction from loaders, test-time feature extraction, ensemble metadata lookup) plus registration of per-contest CLI handler modules on `ContestRegistry`.

## Contents

| Sub-package | Description |
|-------------|-------------|
| `feature_extraction/` | `FeatureExtractionHelper` and test-time / metadata helpers |
| `registry/` | Register and resolve dotted module paths for contest CLI handlers |

Two-stage training (`FeatureExtractionTrainer`) lives in **`level_0_infra.level_3`**, not here.

## Public API

Names from `level_2/__init__.py` (re-exported from sub-packages):

- **FeatureExtractionHelper** — Run `FeatureExtractor.extract_features_and_targets` over a dataloader for a given `dataset_type`.
- **extract_test_features_from_model** — Build feature model + test loader, extract test features, release GPU memory.
- **find_feature_filename_from_ensemble_metadata** — Read `feature_filename` from the first ensemble model’s `model_metadata.json`.
- **register_cli_handlers_module** — Store a contest’s CLI handlers module path on its registry entry.
- **list_contests_with_cli_handlers** — Contest keys that registered a handlers module.
- **get_cli_handlers_module** — `importlib.import_module` for the registered handlers path.

## Dependencies

- **`layers.layer_0_core`:** `get_logger`, `get_device`, `cleanup_gpu_memory`, `FeatureExtractor`, `load_json`, `create_streaming_test_dataloader`.
- **`layers.layer_1_competition.level_0_infra.level_1`:** `create_feature_extraction_model`, `ContestRegistry`.

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_2 import (
    extract_test_features_from_model,
    register_cli_handlers_module,
)

# Contest registration.py (after register_contest):
register_cli_handlers_module(
    "csiro",
    "layers.layer_1_competition.level_1_impl.level_csiro.level_7.handlers",
)

features = extract_test_features_from_model(
    test_csv_path=path_to_csv,
    data_root="/kaggle/input",
    dataset_type="split",
    config=config,
    data_schema=data_schema,
)
```
