# data/processing

## Purpose
Image data processing pipeline: preprocessing operations, augmentation transforms, PyTorch dataset classes, and transform composition.

## Contents
- `preprocessing/` — Resize, normalize, contrast enhance, noise reduce, and image manipulation operations
- `augmentation/` — Gaussian blur, color jitter, geometric, and noise augmentation transform factories
- `transforms/` — Transform pipeline composition (`compose_transform_pipeline`)
- `datasets/` — `BaseImageDataset`, `ImagePathDataset`, and streaming dataset classes

## Public API
All sub-package exports are re-exported from this package.

## Dependencies
- `level_0` — `get_logger`, `get_torch`, `load_image_pil`

## Usage Example
```python
from layers.layer_0_core.level_1.data.processing import compose_transform_pipeline, get_resize_transform, get_normalize_transform
pipeline = compose_transform_pipeline(
    pil_transforms=[get_resize_transform(224)],
    tensor_transforms=[get_normalize_transform()]
)
```