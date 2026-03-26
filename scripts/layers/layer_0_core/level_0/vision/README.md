# Vision

Image loading, patching, transform utilities, and noise reduction for vision models.

## Purpose

Provides image I/O, tiling, transform configuration, noise reduction, and model path classification. All vision primitives consumed by higher-level training and evaluation packages.

## Contents

- `image/` – Image loading (PIL, RGB) and config-driven size resolution, and image patching/tiling
- `minimal_val_transform.py` – Minimal validation-time torchvision transform (Resize + ToTensor + Normalize)
- `model_path.py` – HuggingFace model path detection
- `noise_reduction.py` – Gaussian/median denoising
- `transform_defaults.py` – Default hyperparameter constants for augmentation pipelines
- `transform_mode.py` – `TransformMode` enum (TRAIN / VAL / TEST)

## Public API

- `get_image_size_from_config` – Resolve image size tuple from a config object
- `load_image_pil` – Load an image as a PIL Image
- `load_image_rgb` – Load an image as an RGB numpy array
- `split_image` – Tile an image into non-overlapping patches
- `IMAGENET_MEAN`, `IMAGENET_STD` – Standard ImageNet normalisation constants
- `build_minimal_val_transform` – Build Compose transform: Resize → ToTensor → Normalize(ImageNet)
- `is_huggingface_model_path` – True if the path string refers to a HuggingFace Hub model
- `noise_reduction` – Apply Gaussian or median noise reduction to an image array
- `DEFAULT_BLUR_*`, `DEFAULT_COLOR_*`, `DEFAULT_GEOMETRIC_*`, `DEFAULT_NOISE_*`, `DEFAULT_CONTRAST_*` – Default augmentation constants
- `TransformMode` – Enum: TRAIN, VAL, TEST

## Dependencies

- stdlib: pathlib
- numpy, PIL (Pillow), torchvision

## Usage Example

```python
from level_0 import load_image_pil, build_minimal_val_transform, TransformMode

transform = build_minimal_val_transform((224, 224))
image = load_image_pil("photo.jpg")
tensor = transform(image)
```
