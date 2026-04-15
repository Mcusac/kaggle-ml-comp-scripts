# vision_transforms/augmentation

Augmentation transform registry and presets for training-time data augmentation.

## Purpose

Provides a named registry of augmentation transform builders and four preset augmentation levels (light, medium, heavy, custom) for use in training pipelines.

## Contents

- `presets.py` — `AugmentationPreset`, `PRESET_FUNCS`, `get_light_augmentation`, `get_medium_augmentation`, `get_heavy_augmentation`, `get_custom_augmentation`, `build_augmentation_transforms`
- `registry.py` — `AUGMENTATION_BUILDERS`, `AugmentationBuilder`: registry of config-driven augmentation builders

## Public API

- `AugmentationPreset` — Enum of preset levels: LIGHT, MEDIUM, HEAVY, CUSTOM
- `PRESET_FUNCS` — Dict mapping `AugmentationPreset` to its builder function
- `get_light_augmentation()` — Build light augmentation (geometric only)
- `get_medium_augmentation()` — Build medium augmentation (geometric + color jitter)
- `get_heavy_augmentation()` — Build heavy augmentation (geometric + color jitter + blur)
- `get_custom_augmentation(names)` — Build augmentation from a list of named transform keys
- `build_augmentation_transforms(preset, config)` — Build augmentation pipeline from a preset and config
- `AUGMENTATION_BUILDERS` — Dict mapping augmentation name to `AugmentationBuilder` callable

## Dependencies

- **level_1** — `get_geometric_transform`, `get_color_jitter_transform`, `get_blur_transform`, `get_noise_transform`
- **vision_transforms.preprocessing_registry** — `TransformBuilder` type alias

## Usage Example

```python
from layers.layer_0_core.level_2.vision_transforms.augmentation import get_medium_augmentation, AugmentationPreset

pil_transform, tensor_transform = get_medium_augmentation()
# Apply pil_transform before ToTensor, tensor_transform after
```
