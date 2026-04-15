# vision_transforms

Vision preprocessing pipelines, test-time augmentation (TTA), image cleaning, and augmentation presets. Built on level_1 data processing utilities.

## Purpose

Assembles reusable transform pipelines from individual level_1 building blocks. Provides a composable preprocessing registry, TTA variants, an image-cleaning pipeline, and augmentation presets/registries for training.

## Contents

- `build_transforms.py` — `build_preprocessing_transforms`, `build_simple_transforms`: assemble full torchvision transform pipelines
- `image_cleaning.py` — `ImageCleaningConfig`, `clean_image_with_config`, `clean_image_batch`: configurable OpenCV-based image cleaning
- `preprocessing_registry.py` — `PREPROCESSING_BUILDERS`, `TransformBuilder`: registry of config-driven preprocessing transform builders
- `tta.py` — `TTAVariant`, `build_tta_transforms`, `get_default_tta_variants`, `get_all_tta_variants`: test-time augmentation variants
- `augmentation/` — Augmentation registry and presets (see sub-package)

## Public API

- `build_preprocessing_transforms(image_size, normalize)` — Build a standard preprocessing pipeline (resize, ToTensor, normalize)
- `build_simple_transforms(image_size)` — Build a minimal pipeline without normalization
- `PREPROCESSING_BUILDERS` — Dict mapping preprocessing name to transform builder callable
- `TransformBuilder` — Type alias `Callable[[Any], Optional[Any]]`
- `ImageCleaningConfig` — Dataclass configuring crop ratio and HSV-based inpainting
- `clean_image_with_config(img, config)` — Apply cleaning pipeline to a single image
- `clean_image_batch(images, config)` — Apply cleaning pipeline to a list of images
- `TTAVariant` — Enum of test-time augmentation strategies
- `build_tta_transforms(image_size, variants)` — Build list of transforms for each TTA variant
- `get_default_tta_variants()` — Return the default set of TTA variants
- `get_all_tta_variants()` — Return all available TTA variants

## Dependencies

- **level_0** — `IMAGENET_MEAN`, `IMAGENET_STD`, `noise_reduction`, `get_image_size_from_config`, `get_logger`
- **level_1** — `get_resize_transform`, `get_normalize_transform`, `contrast_enhancement`, `compose_transform_pipeline`

## Usage Example

```python
from layers.layer_0_core.level_2.vision_transforms import build_preprocessing_transforms, TTAVariant, build_tta_transforms

pipe = build_preprocessing_transforms((224, 224), normalize=True)
tta_transforms = build_tta_transforms(
    (224, 224),
    variants=[TTAVariant.ORIGINAL, TTAVariant.H_FLIP],
)
```
