"""CSIRO-specific dataset variant grid for grid search."""

from layers.layer_0_core.level_0 import AVAILABLE_AUGMENTATION, AVAILABLE_PREPROCESSING
from layers.layer_0_core.level_1 import generate_variant_grid


def csiro_dataset_grid():
    """Return CSIRO dataset variant grid (preprocessing × augmentation subsets)."""
    return generate_variant_grid(
        list(AVAILABLE_PREPROCESSING),
        list(AVAILABLE_AUGMENTATION),
        exclude_pre={"resize", "normalize"},
    )
