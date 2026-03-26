"""Vision transforms: preprocessing, transforms (TTA, mode), augmentation."""

from . import augmentation

from .augmentation import *
from .build_transforms import build_preprocessing_transforms, build_simple_transforms
from .image_cleaning import (
    ImageCleaningConfig,
    clean_image_batch,
    clean_image_with_config,
)
from .preprocessing_registry import PREPROCESSING_BUILDERS
from .tta import (
    TTAVariant,
    build_tta_transforms,
    get_all_tta_variants,
    get_default_tta_variants,
)

__all__ = (
    list(augmentation.__all__)
    + ["build_preprocessing_transforms", "build_simple_transforms"]
    + ["ImageCleaningConfig", "clean_image_with_config", "clean_image_batch"]
    + ["PREPROCESSING_BUILDERS"]
    + ["TTAVariant", "build_tta_transforms", "get_default_tta_variants", "get_all_tta_variants"]
)
