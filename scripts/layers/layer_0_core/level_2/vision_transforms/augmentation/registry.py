"""Augmentation transform builder registry using level_1 augmentation APIs."""

from typing import Dict, Callable, Optional, Any, Tuple

from layers.layer_0_core.level_1 import (
    get_geometric_transform,
    get_color_jitter_transform,
    get_blur_transform,
    get_noise_transform
)

AugmentationBuilder = Callable[[Any], Tuple[Optional[Any], Optional[Any]]]


def _get_geometric_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]:
    """Get geometric transformation augmentation (PIL transform)."""
    return (get_geometric_transform(), None)


def _get_color_jitter_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]:
    """Get color jittering augmentation (PIL transform)."""
    return (get_color_jitter_transform(), None)


def _get_blurring_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]:
    """Get blurring augmentation (PIL transform)."""
    return (get_blur_transform(), None)


def _get_noise_addition_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]:
    """Get noise addition augmentation (tensor transform)."""
    return (None, get_noise_transform())


AUGMENTATION_BUILDERS: Dict[str, AugmentationBuilder] = {
    "geometric_transformations": _get_geometric_augmentation,
    "color_jittering": _get_color_jitter_augmentation,
    "blurring": _get_blurring_augmentation,
    "noise_addition": _get_noise_addition_augmentation,
}
