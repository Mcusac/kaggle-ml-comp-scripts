# level_6.prediction

## Purpose

Prediction pipeline for vision and tabular checkpoints, plus a streaming test DataLoader built from a CSV path.

## Contents

- `predict_pipeline.py` — `PredictPipeline` for vision and tabular models
- `streaming_test_dataloader.py` — `create_streaming_test_dataloader` (CSV + streaming dataset; not the level_4 DataFrame-based `create_test_dataloader`)

## Public API

| Name | Description |
|------|-------------|
| `PredictPipeline` | Prediction pipeline for vision or tabular models |
| `create_streaming_test_dataloader` | Build test `DataLoader` from CSV path, data root, and column metadata |

## Dependencies

- **level_0**: `ensure_dir`, `get_logger`, `get_torch`
- **level_1**: `validate_config_section_exists`, `BasePipeline`, `get_device`
- **level_2**: `VisionPredictor`
- **level_3**: `TTAPredictor`
- **level_4**: `create_test_dataloader` (DataFrame-based vision loader), `create_vision_model`, `load_pickle`
- **level_5**: `load_and_validate_test_data`, `prepare_test_dataframe_with_dummy_targets` (streaming loader only)

## Usage Example

```python
from layers.layer_0_core.level_6 import PredictPipeline, create_streaming_test_dataloader

pipeline = PredictPipeline(config, model_path="model.pkl", model_type="tabular", X_test=X_test)
pipeline.setup()
result = pipeline.execute()

loader = create_streaming_test_dataloader(
    test_csv_path="test.csv",
    data_root="/data",
    image_path_column="image_id",
    primary_targets=["target_a"],
    image_size=(224, 224),
)
```
