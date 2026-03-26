"""CSIRO derived target computation (primary -> GDM, Dry_Total)."""

import numpy as np

NUM_PRIMARY_TARGETS = 3


def compute_derived_targets(primary_targets: np.ndarray) -> np.ndarray:
    """
    Compute derived targets (GDM_g and Dry_Total_g) from primary targets.

    Args:
        primary_targets: Array of shape (N, 3) with primary target values
                        [Dry_Green_g, Dry_Clover_g, Dry_Dead_g]

    Returns:
        Array of shape (N, 5) with all targets
        [Dry_Green_g, Dry_Clover_g, Dry_Dead_g, GDM_g, Dry_Total_g]

    Raises:
        ValueError: If input shape is incorrect.
    """
    if primary_targets.ndim != 2:
        raise ValueError(
            f"Expected 2D array, got shape: {primary_targets.shape}"
        )

    if primary_targets.shape[1] != NUM_PRIMARY_TARGETS:
        raise ValueError(
            f"Expected {NUM_PRIMARY_TARGETS} primary targets, "
            f"got {primary_targets.shape[1]}"
        )

    green = primary_targets[:, 0]
    clover = primary_targets[:, 1]
    dead = primary_targets[:, 2]

    gdm = green + clover
    total = green + clover + dead

    all_targets = np.column_stack([
        green, clover, dead,
        gdm, total,
    ])

    return all_targets
