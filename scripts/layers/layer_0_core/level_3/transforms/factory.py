"""
Config-driven transform factory. Bridges config objects to level_2 vision transforms.

NOTE: This is the config-driven variant of build_tta_transforms.
level_2/vision_transforms/tta.build_tta_transforms takes a transform list;
this module takes a config object.
"""

import torchvision.transforms as transforms

from typing import Any, List, Optional, Tuple, Union

from layers.layer_0_core.level_0 import (
    AVAILABLE_TTA_VARIANTS,
    DEFAULT_BLUR_SIGMA,
    DEFAULT_COLOR_BRIGHTNESS,
    DEFAULT_COLOR_CONTRAST,
    DEFAULT_COLOR_HUE,
    DEFAULT_COLOR_SATURATION,
    DEFAULT_TTA_VARIANTS,
    IMAGENET_MEAN,
    IMAGENET_STD,
    get_image_size_from_config,
    get_logger,
)
from layers.layer_0_core.level_1 import (
    compose_transform_pipeline,
    get_color_jitter_transform,
    get_noise_transform,
    get_normalize_transform,
    get_resize_transform,
)
from layers.layer_0_core.level_2 import PREPROCESSING_BUILDERS, build_augmentation_transforms

logger = get_logger(__name__)


def _build_deterministic_augmentations_from_list(
    augmentation_list: List[str],
) -> Tuple[List[Any], List[Any]]:
    """Build PIL and tensor transforms for blurring, color_jittering, noise_addition."""
    pil_list: List[Any] = []
    tensor_list: List[Any] = []
    for aug_name in augmentation_list:
        if aug_name == "blurring":
            sigma_min, sigma_max = DEFAULT_BLUR_SIGMA
            fixed = (sigma_min + sigma_max) / 2.0
            pil_list.append(
                transforms.GaussianBlur(kernel_size=5, sigma=(fixed, fixed))
            )
        elif aug_name == "color_jittering":
            pil_list.append(
                get_color_jitter_transform(
                    brightness=DEFAULT_COLOR_BRIGHTNESS,
                    contrast=DEFAULT_COLOR_CONTRAST,
                    saturation=DEFAULT_COLOR_SATURATION,
                    hue=DEFAULT_COLOR_HUE,
                )
            )
        elif aug_name == "noise_addition":
            tensor_list.append(get_noise_transform())
        elif aug_name == "geometric_transformations":
            logger.debug(
                "Skipping 'geometric_transformations' (handled by variant)"
            )
        else:
            logger.warning("Unknown augmentation '%s', skipping", aug_name)
    return (pil_list, tensor_list)


def _build_preprocessing_transforms_from_config(
    config: Union[Any, dict],
    preprocessing_list: List[str],
) -> List[Any]:
    """Build list of PIL preprocessing transforms from config and preprocessing_list."""
    result = []
    for name in preprocessing_list:
        builder = PREPROCESSING_BUILDERS.get(name)
        if builder is not None:
            t = builder(config)
            if t is not None:
                result.append(t)
    if not result:
        image_size = get_image_size_from_config(config)
        if image_size is not None:
            result.append(get_resize_transform(image_size))
    return result


def _build_augmentation_transforms_from_config(
    config: Union[Any, dict],
    augmentation_list: List[str],
    include_augmentation: bool,
) -> Tuple[List[Any], List[Any]]:
    """Build (pil_transforms, tensor_transforms) from config and augmentation_list."""
    if not include_augmentation or not augmentation_list:
        return [], []
    preset = augmentation_list[0] if augmentation_list else "none"
    if preset in ("none", "light", "medium", "heavy"):
        aug_list = build_augmentation_transforms(preset)
        return (aug_list, [])
    return _build_deterministic_augmentations_from_list(augmentation_list)


def _build_tensor_transforms(config: Union[Any, dict]) -> List[Any]:
    """Build tensor transforms (normalization) from config."""
    mean = IMAGENET_MEAN
    std = IMAGENET_STD
    if isinstance(config, dict):
        mean = config.get("mean", mean)
        std = config.get("std", std)
    elif hasattr(config, "data"):
        mean = getattr(config.data, "mean", mean)
        std = getattr(config.data, "std", std)
    return [get_normalize_transform(mean, std)]


def _build_base_transform(
    config: Union[Any, dict],
    include_augmentation: bool = False,
) -> transforms.Compose:
    """Build base transform pipeline from config (shared by train and val)."""
    preprocessing_list = []
    if isinstance(config, dict):
        preprocessing_list = config.get("preprocessing_list", [])
    elif hasattr(config, "data") and hasattr(config.data, "preprocessing_list"):
        preprocessing_list = config.data.preprocessing_list or []

    pil_transforms = _build_preprocessing_transforms_from_config(
        config, preprocessing_list
    )
    if not isinstance(pil_transforms, list):
        pil_transforms = [pil_transforms] if pil_transforms else []

    augmentation_list = []
    if include_augmentation:
        if isinstance(config, dict):
            augmentation_list = config.get("augmentation_list", [])
        elif hasattr(config, "data") and hasattr(config.data, "augmentation_list"):
            augmentation_list = config.data.augmentation_list or []

    aug_pil, aug_tensor = _build_augmentation_transforms_from_config(
        config, augmentation_list, include_augmentation
    )
    tensor_transforms = _build_tensor_transforms(config)

    all_pil = (pil_transforms or []) + (aug_pil or [])
    all_tensor = (aug_tensor or []) + (tensor_transforms or [])
    return compose_transform_pipeline(
        pil_transforms=all_pil,
        tensor_transforms=all_tensor,
    )


def build_train_transform(config: Union[Any, dict]) -> transforms.Compose:
    """Build training transform pipeline from config with augmentation enabled."""
    return _build_base_transform(config, include_augmentation=True)


def build_val_transform(config: Union[Any, dict]) -> transforms.Compose:
    """Build validation transform pipeline from config without augmentation."""
    return _build_base_transform(config, include_augmentation=False)


def _apply_geometric_variant(
    variant: str,
    variant_pil_transforms: List,
) -> None:
    """Apply geometric transforms for a TTA variant."""
    if variant == "original":
        pass
    elif variant == "h_flip":
        variant_pil_transforms.append(transforms.RandomHorizontalFlip(p=1.0))
    elif variant == "v_flip":
        variant_pil_transforms.append(transforms.RandomVerticalFlip(p=1.0))
    elif variant == "both_flips":
        variant_pil_transforms.append(transforms.RandomHorizontalFlip(p=1.0))
        variant_pil_transforms.append(transforms.RandomVerticalFlip(p=1.0))
    elif variant == "rotate_90":
        variant_pil_transforms.append(
            transforms.RandomRotation(degrees=(90, 90))
        )
    elif variant == "rotate_270":
        variant_pil_transforms.append(
            transforms.RandomRotation(degrees=(270, 270))
        )


def _apply_deterministic_augmentations(
    augmentation_list: List[str],
    variant_pil_transforms: List,
    variant_tensor_transforms: List,
) -> None:
    """Apply augmentations from augmentation_list deterministically to variant lists."""
    pil_list, tensor_list = _build_deterministic_augmentations_from_list(
        augmentation_list
    )
    variant_pil_transforms.extend(pil_list)
    variant_tensor_transforms.extend(tensor_list)


def _build_single_tta_variant(
    variant: str,
    base_pil_transforms: List,
    augmentation_list: List[str],
    config: Union[Any, dict],
) -> transforms.Compose:
    """Build a single TTA variant transform pipeline."""
    variant_pil_transforms = base_pil_transforms.copy()
    variant_tensor_transforms = []
    _apply_geometric_variant(variant, variant_pil_transforms)
    _apply_deterministic_augmentations(
        augmentation_list, variant_pil_transforms, variant_tensor_transforms
    )
    tensor_transforms = _build_tensor_transforms(config)
    all_pil = variant_pil_transforms
    all_tensor = variant_tensor_transforms + tensor_transforms
    return compose_transform_pipeline(
        pil_transforms=all_pil,
        tensor_transforms=all_tensor,
    )


def build_tta_transforms(
    config: Union[Any, dict],
    tta_variants: Optional[List[str]] = None,
) -> List[transforms.Compose]:
    """
    Build TTA transforms using same augmentation builders as training.
    Config-driven variant (level_2 tta.build_tta_transforms takes transform list).
    """
    if tta_variants is None:
        tta_variants = list(DEFAULT_TTA_VARIANTS)
    invalid = set(tta_variants) - AVAILABLE_TTA_VARIANTS
    if invalid:
        raise ValueError(
            f"Invalid TTA variants: {invalid}. "
            f"Available: {AVAILABLE_TTA_VARIANTS}"
        )
    preprocessing_list = []
    if isinstance(config, dict):
        preprocessing_list = config.get("preprocessing_list", [])
    elif hasattr(config, "data") and hasattr(config.data, "preprocessing_list"):
        preprocessing_list = config.data.preprocessing_list or []

    base_pil = _build_preprocessing_transforms_from_config(
        config, preprocessing_list
    )
    if not isinstance(base_pil, list):
        base_pil = [base_pil] if base_pil else []

    augmentation_list = []
    if isinstance(config, dict):
        augmentation_list = config.get("augmentation_list", [])
    elif hasattr(config, "data") and hasattr(config.data, "augmentation_list"):
        augmentation_list = config.data.augmentation_list or []

    transforms_list = [
        _build_single_tta_variant(v, base_pil, augmentation_list, config)
        for v in tta_variants
    ]
    logger.info("Built %s TTA variants: %s", len(transforms_list), ", ".join(tta_variants))
    if augmentation_list:
        logger.info(
            "Applying augmentations deterministically: %s",
            ", ".join(augmentation_list),
        )
    return transforms_list
