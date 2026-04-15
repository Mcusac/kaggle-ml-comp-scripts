"""NumPy array guards."""

import numpy as np

from layers.layer_0_core.level_0 import DataValidationError


def check_array_finite(
    array: np.ndarray,
    *,
    name: str = "array",
) -> None:
    """
    Ensure array does not contain NaN or infinite values.

    Args:
        array: NumPy array to validate
        name: Name used in error message

    Raises:
        DataValidationError: If invalid values are found
    """
    nan_mask = np.isnan(array)
    if nan_mask.any():
        raise DataValidationError(
            f"{name} contains {nan_mask.sum()} NaN values"
        )

    inf_mask = np.isinf(array)
    if inf_mask.any():
        raise DataValidationError(
            f"{name} contains {inf_mask.sum()} infinite values"
        )