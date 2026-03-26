"""Test-time augmentation transforms."""

import torchvision.transforms as transforms

from typing import List, Union, Tuple
from enum import Enum

from layers.layer_0_core.level_0 import get_logger, IMAGENET_MEAN, IMAGENET_STD
from layers.layer_0_core.level_1 import get_resize_transform, get_normalize_transform, compose_transform_pipeline

logger = get_logger(__name__)


class TTAVariant(Enum):
    """TTA variant types."""
    ORIGINAL = "original"
    H_FLIP = "h_flip"
    V_FLIP = "v_flip"
    HV_FLIP = "hv_flip"
    ROTATE_90 = "rotate_90"
    ROTATE_180 = "rotate_180"
    ROTATE_270 = "rotate_270"


def _convert_variants_to_enums(
    variants: List[Union[TTAVariant, str]]
) -> List[TTAVariant]:
    """Convert string variants to TTAVariant enums."""
    result = []
    for v in variants:
        if isinstance(v, str):
            try:
                result.append(TTAVariant(v))
            except ValueError:
                logger.warning(f"Unknown TTA variant: {v}, skipping")
        elif isinstance(v, TTAVariant):
            result.append(v)
        else:
            logger.warning(f"Invalid TTA variant type: {type(v)}, skipping")
    return result


def _build_variant_transform(
    variant: TTAVariant,
    base_pil_transforms: List,
    tensor_transforms: List,
) -> transforms.Compose:
    """Build transform pipeline for a single TTA variant."""

    variant_pil = list(base_pil_transforms)
    if variant == TTAVariant.ORIGINAL:
        pass
    elif variant == TTAVariant.H_FLIP:
        variant_pil.append(transforms.RandomHorizontalFlip(p=1.0))
    elif variant == TTAVariant.V_FLIP:
        variant_pil.append(transforms.RandomVerticalFlip(p=1.0))
    elif variant == TTAVariant.HV_FLIP:
        variant_pil.append(transforms.RandomHorizontalFlip(p=1.0))
        variant_pil.append(transforms.RandomVerticalFlip(p=1.0))
    elif variant == TTAVariant.ROTATE_90:
        variant_pil.append(transforms.RandomRotation(degrees=(90, 90)))
    elif variant == TTAVariant.ROTATE_180:
        variant_pil.append(transforms.RandomRotation(degrees=(180, 180)))
    elif variant == TTAVariant.ROTATE_270:
        variant_pil.append(transforms.RandomRotation(degrees=(270, 270)))
    return compose_transform_pipeline(
        pil_transforms=variant_pil,
        tensor_transforms=tensor_transforms,
        include_to_tensor=True,
    )


def build_tta_transforms(
    image_size: Union[int, Tuple[int, int]],
    variants: List[Union[TTAVariant, str]] = None,
    normalize: bool = True,
    mean: Tuple[float, float, float] = IMAGENET_MEAN,
    std: Tuple[float, float, float] = IMAGENET_STD
) -> List[transforms.Compose]:
    """
    Build list of TTA transform variants for test-time augmentation.
    """
    if variants is None:
        variants = [TTAVariant.ORIGINAL, TTAVariant.H_FLIP, TTAVariant.V_FLIP]

    variant_enums = _convert_variants_to_enums(variants)
    base_pil_transforms = [get_resize_transform(image_size)]
    tensor_transforms = []
    if normalize:
        tensor_transforms.append(get_normalize_transform(mean, std))

    tta_transform_list = []
    for variant in variant_enums:
        tta_transform_list.append(
            _build_variant_transform(variant, base_pil_transforms, tensor_transforms)
        )
        logger.debug(f"Built TTA variant: {variant.value}")

    logger.info(f"Built {len(tta_transform_list)} TTA transform variants")
    return tta_transform_list


def get_default_tta_variants() -> List[TTAVariant]:
    """Get default TTA variants (original, h_flip, v_flip)."""
    return [TTAVariant.ORIGINAL, TTAVariant.H_FLIP, TTAVariant.V_FLIP]


def get_all_tta_variants() -> List[TTAVariant]:
    """Get all available TTA variants."""
    return list(TTAVariant)
