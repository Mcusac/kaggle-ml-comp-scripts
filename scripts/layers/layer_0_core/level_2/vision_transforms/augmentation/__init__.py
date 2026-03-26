"""Vision augmentation: registry, presets, and preset selector."""

from .presets import (
    get_light_augmentation,
    get_medium_augmentation,
    get_heavy_augmentation,
    get_custom_augmentation,
    AugmentationPreset,
    PRESET_FUNCS,
    build_augmentation_transforms,
)
from .registry import AUGMENTATION_BUILDERS

__all__ = [
    "get_light_augmentation",
    "get_medium_augmentation",
    "get_heavy_augmentation",
    "get_custom_augmentation",
    "AugmentationPreset",
    "PRESET_FUNCS",
    "build_augmentation_transforms",
    "AUGMENTATION_BUILDERS",
]
