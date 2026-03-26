# level_6.prediction

## Purpose

Prediction pipeline and streaming test dataloader creation.

## Contents

- `predict_pipeline.py` — PredictPipeline for vision and tabular models
- `create_test_dataloader.py` — Streaming test DataLoader (distinct from level_4 DataFrame-based version)

## Public API

| Name | Description |
|------|-------------|
| `PredictPipeline` | Prediction pipeline for vision/tabular |
| `create_test_dataloader` | Create test DataLoader from CSV path (streaming) |

## Dependencies

- **level_0**: ensure_dir, get_logger, get_torch
- **level_1**: validate_config_section_exists, BasePipeline, get_device
- **level_2**: VisionPredictor, build_preprocessing_transforms, create_dataloader_from_dataset, create_streaming_dataset_for_test
- **level_3**: TTAPredictor
- **level_4**: create_test_dataloader (DataFrame-based), create_vision_model, load_pickle
- **level_5**: load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets

## Usage Example

```python
from level_6 import PredictPipeline, create_test_dataloader

# Prediction pipeline
pipeline = PredictPipeline(config, model_path="model.pkl", model_type="tabular", X_test=X_test)
pipeline.setup()
result = pipeline.execute()

# Streaming test dataloader (level_6 version)
loader = create_test_dataloader(
    test_csv_path="test.csv",
    data_root="/data",
    image_path_column="image_id",
    primary_targets=["target_a"],
    image_size=(224, 224),
)
```
