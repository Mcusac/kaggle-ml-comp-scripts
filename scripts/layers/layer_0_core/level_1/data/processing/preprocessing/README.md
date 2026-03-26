# data/processing/preprocessing

## Purpose
Image preprocessing operations: resizing, normalization, contrast enhancement, noise reduction, and low-level image manipulation.

## Contents
- `resizing.py` — `resize` (PIL), `get_resize_transform` (torchvision)
- `normalization.py` — `normalize` (tensor), `get_normalize_transform` (torchvision), with ImageNet defaults
- `contrast_enhancement.py` — `contrast_enhancement`: histogram equalization or CLAHE
- `noise_reduction.py` — `noise_reduction`: Gaussian blur, bilateral filter, or median filter
- `image_base.py` — `crop_relative_height`, `inpaint_by_hsv_range`: low-level pixel manipulation

## Public API
- `resize(image, size, interpolation)` → resized PIL Image
- `get_resize_transform(size, interpolation)` → `transforms.Resize`
- `normalize(tensor, mean, std)` → normalized tensor
- `get_normalize_transform(mean, std)` → `transforms.Normalize`
- `contrast_enhancement(image, method)` → enhanced image
- `noise_reduction(image, method, kernel_size)` → denoised image
- `crop_relative_height(img, keep_ratio)` → cropped numpy array
- `inpaint_by_hsv_range(img, lower, upper, ...)` → inpainted numpy array

## Dependencies
- `level_0` — `get_logger`, `get_torch`

## Usage Example
```python
from level_1.data.processing.preprocessing import get_resize_transform, get_normalize_transform
resize_t = get_resize_transform(224)
norm_t = get_normalize_transform()
```