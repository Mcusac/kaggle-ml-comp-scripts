# Vision / Image

Image loading and patching utilities.

## Purpose

Loads images from disk in PIL and RGB formats, resolves image size from config objects, and tiles images into non-overlapping patches.

## Contents

- `config.py` – `get_image_size_from_config`: resolve image (height, width) from a config object
- `loading.py` – `load_image_pil`, `load_image_rgb`: load images as PIL Image or RGB numpy array
- `patching.py` – `split_image`: tile an image into a grid of non-overlapping patches

## Public API

- `get_image_size_from_config(config)` – Return `(height, width)` tuple from config
- `load_image_pil(path)` – Return a PIL Image loaded from `path`
- `load_image_rgb(path)` – Return an RGB uint8 numpy array loaded from `path`
- `split_image(image, patch_size)` – Return a list of image patches

## Dependencies

- stdlib: pathlib
- numpy, PIL (Pillow)

## Usage Example

```python
from level_0.vision.image import load_image_pil, split_image

image = load_image_pil("photo.jpg")
patches = split_image(image, patch_size=224)
```
