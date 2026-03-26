"""Series validation.

Validation utilities for pandas Series.
"""

import pandas as pd

from level_0 import DataValidationError
from level_1 import check_not_none, check_min_collection_length

def validate_series(
    series: pd.Series,
    min_length: int = 1,    
    check_nan: bool = False,
    unique: bool = False,
    name: str = "series"
) -> None:
    """
    Validate pandas Series.
    
    Args:
        series: Series to validate
        min_length: Minimum length required (default: 1)
        check_nan: If True, raise error if series contains NaN values
        unique: If True, raise error if series contains duplicate values
        name: Name of Series for error messages
        
    Raises:
        DataValidationError: If validation fails
        
    Example:
        >>> import pandas as pd
        >>> s = pd.Series([1, 2, 3, 4, 5])
        >>> validate_series(s, min_length=3, unique=True)
    """
    check_not_none(series, name)
    check_min_collection_length(series, min_length, name)
    
    if check_nan and series.isna().any():
        nan_count = series.isna().sum()
        raise DataValidationError(f"{name} contains {nan_count} NaN values")
    
    if unique and series.duplicated().any():
        dup_count = series.duplicated().sum()
        raise DataValidationError(
            f"{name} contains {dup_count} duplicate values (expected all unique)"
        )