# data/processing/augmentation

## Purpose
Torchvision-compatible augmentation transform factories. All factories accept caller-provided parameters; defaults exist but contest layers provide their own values.

## Contents
- `blur.py` — `get_blur_transform`: Gaussian blur, enforces odd kernel size
- `color.py` — `get_color_jitter_transform`: brightness, contrast, saturation, hue jitter
- `geometric.py` — `get_geometric_transform`: rotation, translation, scale, shear via `RandomAffine`
- `noise.py` — `AddGaussianNoise` module and `get_noise_transform` factory

## Public API
- `get_blur_transform(kernel_size, sigma, p)` → `transforms.GaussianBlur` or `RandomApply`
- `get_color_jitter_transform(brightness, contrast, saturation, hue, p)` → `ColorJitter` or `RandomApply`
- `get_geometric_transform(degrees, translate, scale, shear, interpolation, fill, p)` → `RandomAffine` or `RandomApply`
- `AddGaussianNoise(mean, std, p)` — `nn.Module` that adds Gaussian noise to tensors
- `get_noise_transform(mean, std, p)` → `AddGaussianNoise`

## Dependencies
- `level_0` — `get_logger`, `get_torch`

## Usage Example
```python
from level_1.data.processing.augmentation import get_blur_transform, get_geometric_transform
blur = get_blur_transform(kernel_size=3, p=0.5)
geom = get_geometric_transform(degrees=15, p=0.8)
```