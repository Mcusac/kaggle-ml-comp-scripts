"""Array validation.
Validation utilities for numpy arrays including model outputs.
"""

import numpy as np

from typing import Optional, Tuple

from level_0 import DataValidationError
from level_1 import check_not_none, check_array_finite

def validate_array(
    array: np.ndarray,
    expected_shape: Optional[Tuple[Optional[int], ...]] = None,
    check_nan: bool = False,
    check_inf: bool = False,
    name: str = "array"
) -> None:
    """
    Validate numpy array shape and values.
    
    Args:
        array: Array to validate
        expected_shape: Expected shape. Use None for variable dimensions.
                       Example: (None, 10) allows any first dimension, fixed 10 second
        check_nan: If True, raise error if array contains NaN values
        check_inf: If True, raise error if array contains infinite values
        name: Name of array for error messages
        
    Raises:
        DataValidationError: If validation fails for any reason:
            - Array is None
            - Shape doesn't match expected (when specified)
            - Contains NaN values (when check_nan=True)
            - Contains infinite values (when check_inf=True)
            
    Example:
        >>> import numpy as np
        >>> arr = np.array([[1, 2], [3, 4]])
        >>> validate_array(arr, expected_shape=(2, 2))
        >>> validate_array(arr, expected_shape=(None, 2), check_nan=True)
    """
    check_not_none(array, name)
    
    if expected_shape is not None:
        if len(expected_shape) != array.ndim:
            raise DataValidationError(
                f"{name} shape specification has {len(expected_shape)} dimensions, "
                f"but array has {array.ndim} dimensions"
            )
        
        for i, (actual, expected) in enumerate(zip(array.shape, expected_shape)):
            if expected is not None and actual != expected:
                raise DataValidationError(
                    f"{name} dimension {i} has size {actual}, expected {expected}. "
                    f"Full shape: {array.shape}, expected: {expected_shape}"
                )
    
    check_array_finite(array, check_nan=check_nan, check_inf=check_inf, name=name)


def validate_model_output(
    predictions: np.ndarray,
    expected_shape: Optional[Tuple[int, ...]] = None,
    check_nan: bool = True,
    check_inf: bool = True
) -> None:
    """
    Validate model predictions/output.
    
    This is a convenience wrapper around validate_array with stricter defaults
    (NaN and inf checking enabled by default) for model outputs.
    
    Args:
        predictions: Model predictions array
        expected_shape: Expected exact shape (no None dimensions allowed)
        check_nan: Check for NaN values (default: True)
        check_inf: Check for infinite values (default: True)
        
    Raises:
        DataValidationError: If validation fails
        
    Example:
        >>> predictions = model.predict(X_test)
        >>> validate_model_output(predictions, expected_shape=(100, 3))
    """
    check_not_none(predictions, "predictions")
    
    if expected_shape is not None and predictions.shape != expected_shape:
        raise DataValidationError(
            f"Prediction shape {predictions.shape} doesn't match expected {expected_shape}"
        )
    
    check_array_finite(
        predictions,
        check_nan=check_nan,
        check_inf=check_inf,
        name="predictions"
    )


def validate_paired_arrays(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    allow_different_shapes: bool = False,
    name_true: str = "y_true",
    name_pred: str = "y_pred",
) -> None:
    """
    Validate paired arrays for metric calculation (e.g. y_true, y_pred).

    Args:
        y_true: Ground truth array
        y_pred: Prediction array
        allow_different_shapes: If True, skip shape-match check (e.g. ROC-AUC with y_pred_proba)
        name_true: Name for y_true in error messages
        name_pred: Name for y_pred in error messages

    Raises:
        DataValidationError: If validation fails:
            - Either array is None
            - Either array is not a numpy ndarray
            - Shapes differ when allow_different_shapes=False
            - y_true is empty
    """
    check_not_none(y_true, name_true)
    check_not_none(y_pred, name_pred)

    if not isinstance(y_true, np.ndarray):
        raise DataValidationError(
            f"{name_true} must be numpy array, got {type(y_true)}"
        )
    if not isinstance(y_pred, np.ndarray):
        raise DataValidationError(
            f"{name_pred} must be numpy array, got {type(y_pred)}"
        )

    if not allow_different_shapes and y_true.shape != y_pred.shape:
        raise DataValidationError(
            f"Shape mismatch: {name_true} {y_true.shape} != {name_pred} {y_pred.shape}"
        )

    if y_true.size == 0:
        raise DataValidationError(
            f"Cannot calculate metrics on empty {name_true} array"
        )