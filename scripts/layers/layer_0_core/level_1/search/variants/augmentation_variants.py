"""Preprocessor and augmentation variant grid generation."""

from typing import Any, List, Optional, Set, Tuple

from level_0 import generate_power_set


def generate_variant_grid(
    preprocessors: List[Any],
    augmenters: List[Any],
    excluded_preprocessors: Optional[Set[Any]] = None,
) -> List[Tuple[List[Any], List[Any]]]:
    """
    Generate all (preprocessor combination, augmenter combination) variant pairs.

    Takes the power set of preprocessors and the power set of augmenters,
    then returns their cartesian product. Each element of the result is a
    tuple of (preprocessor_list, augmenter_list) representing one variant.

    Args:
        preprocessors: All available preprocessors to combine.
        augmenters: All available augmenters to combine.
        excluded_preprocessors: Preprocessors to exclude before generating
            combinations. Defaults to no exclusions.

    Returns:
        List of (preprocessor_subset, augmenter_subset) tuples covering
        every combination. Includes the empty-set case for both axes,
        so the total count is 2^|preprocessors| * 2^|augmenters|
        (after exclusions).
    """
    excluded = excluded_preprocessors or set()
    active_preprocessors = [p for p in preprocessors if p not in excluded]

    pre_sets = generate_power_set(active_preprocessors)
    aug_sets = generate_power_set(augmenters)

    return [
        (list(pre), list(aug))
        for pre in pre_sets
        for aug in aug_sets
    ]