# level_3 transforms

Config-driven transform factory that bridges config objects to level_2 vision transforms. Provides train, validation, and TTA transform pipelines built from configuration.

## Purpose

Builds torchvision transform pipelines from config objects or dicts. This is the config-driven variant; level_2 `build_tta_transforms` takes `image_size` and `variants` directly.

## Contents

- `factory.py` — `build_train_transform`, `build_val_transform`, `build_tta_transforms`; internal helpers for preprocessing, augmentation, and TTA variant construction from config.

## Public API

- `build_train_transform(config)` — Build training transform pipeline with augmentation enabled.
- `build_val_transform(config)` — Build validation transform pipeline without augmentation.
- `build_tta_transforms(config, tta_variants=None)` — Build list of TTA variant transforms using same augmentation builders as training. Uses `level_0` `DEFAULT_TTA_VARIANTS` and `AVAILABLE_TTA_VARIANTS` for variant validation.

## Dependencies

- **level_0** — `DEFAULT_BLUR_SIGMA`, `DEFAULT_COLOR_*`, `DEFAULT_TTA_VARIANTS`, `AVAILABLE_TTA_VARIANTS`, `IMAGENET_MEAN`, `IMAGENET_STD`, `get_image_size_from_config`, `get_logger`.
- **level_1** — `compose_transform_pipeline`, `get_color_jitter_transform`, `get_noise_transform`, `get_normalize_transform`, `get_resize_transform`.
- **level_2** — `PREPROCESSING_BUILDERS`, `build_augmentation_transforms`.

## Usage Example

```python
from level_3 import build_train_transform, build_val_transform, build_tta_transforms

train_tf = build_train_transform(config)
val_tf = build_val_transform(config)
tta_list = build_tta_transforms(config, tta_variants=["original", "h_flip", "v_flip"])
```
