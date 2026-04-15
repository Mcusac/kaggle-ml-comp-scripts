# data/processing/datasets

## Purpose
PyTorch Dataset classes for image data: DataFrame-backed loading and streaming iteration.

## Contents
- `image_datasets.py` — `BaseImageDataset` (DataFrame + image dir), `ImagePathDataset` (path list)
- `streaming_datasets.py` — `BaseStreamingDataset`, `StreamingDataset`, `StreamingSplitDataset`

## Public API
- `BaseImageDataset(data, image_dir, image_col, target_cols, transform, image_ext)` — map-style dataset
- `ImagePathDataset(image_paths, transform)` — inference dataset from path list
- `BaseStreamingDataset` — abstract iterable base; subclass and implement `_load_item`
- `StreamingDataset` — yields `(image_tensor, targets_tensor)` tuples
- `StreamingSplitDataset` — yields `(left_tensor, right_tensor, targets_tensor)` for split images

## Dependencies
- `level_0` — `get_logger`, `get_torch`, `load_image_pil`

## Usage Example
```python
from layers.layer_0_core.level_1.data.processing.datasets import BaseImageDataset
dataset = BaseImageDataset(df, image_dir="images/", target_cols=["label"])
```