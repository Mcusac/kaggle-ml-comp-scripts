"""Dataset variant utilities (generic; contest-specific grids live in contest layer)."""

from typing import List, Tuple

from level_0 import (
    get_logger, 
    generate_power_set, 
    AVAILABLE_PREPROCESSING, 
    AVAILABLE_AUGMENTATION
)
logger = get_logger(__name__)

_ALWAYS_APPLIED_PREPROCESSING: frozenset = frozenset({"resize", "normalize"})


def _get_preprocessing_and_augmentation_options() -> Tuple[List[str], List[str]]:
    """Return optional preprocessing and augmentation options for variant grids."""
    all_preprocessing = sorted(list(AVAILABLE_PREPROCESSING))
    preprocessing_options = [
        opt for opt in all_preprocessing
        if opt not in _ALWAYS_APPLIED_PREPROCESSING
    ]
    augmentation_options = sorted(list(AVAILABLE_AUGMENTATION))
    return preprocessing_options, augmentation_options


def get_max_augmentation_variant() -> Tuple[List[str], List[str]]:
    """Return the maximal variant: all optional preprocessing and augmentation options."""
    preprocessing_options, augmentation_options = _get_preprocessing_and_augmentation_options()

    logger.info("Max augmentation variant:")
    logger.info("  Preprocessing: %s", preprocessing_options)
    logger.info("  Augmentation: %s", augmentation_options)

    return preprocessing_options, augmentation_options


def get_dataset_variant_grid() -> List[Tuple[List[str], List[str]]]:
    """Generate power-set grid of all preprocessing and augmentation combinations."""
    preprocessing_options, augmentation_options = _get_preprocessing_and_augmentation_options()

    preprocessing_combinations = generate_power_set(preprocessing_options)
    augmentation_combinations = generate_power_set(augmentation_options)

    num_optional_preprocessing = len(preprocessing_options)
    num_augmentation = len(augmentation_options)
    num_preprocessing_combinations = len(preprocessing_combinations)
    num_augmentation_combinations = len(augmentation_combinations)
    total_combinations = num_preprocessing_combinations * num_augmentation_combinations

    grid = [
        (list(prep_combo), list(aug_combo))
        for prep_combo in preprocessing_combinations
        for aug_combo in augmentation_combinations
    ]

    logger.info("Generated dataset variant grid: %d combinations", total_combinations)
    logger.info(
        "  Optional preprocessing methods: %d -> %d combinations",
        num_optional_preprocessing,
        num_preprocessing_combinations,
    )
    logger.info(
        "  Augmentation methods: %d -> %d combinations",
        num_augmentation,
        num_augmentation_combinations,
    )
    logger.info(
        "  Total: %d x %d = %d",
        num_preprocessing_combinations,
        num_augmentation_combinations,
        total_combinations,
    )

    return grid