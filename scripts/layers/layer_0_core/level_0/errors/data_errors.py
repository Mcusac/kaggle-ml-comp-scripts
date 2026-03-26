"""Data-related exceptions.

Hierarchy:
- DataError (base)
  - DataLoadError (file loading failed)
  - DataValidationError (data structure/content invalid)
  - DataProcessingError (data transformation failed)
"""


class DataError(Exception):
    """Base exception for data errors.

    Raised when data-related operations fail.
    Subclasses provide more specific error categories.
    """
    pass


class DataLoadError(DataError):
    """Raised when data cannot be loaded.

    Examples:
    - File not found
    - Corrupted file format
    - Unsupported file type
    - Read permission denied

    Usage:
        >>> try:
        ...     df = pd.read_csv(path)
        ... except Exception as e:
        ...     raise DataLoadError(f"Failed to load CSV {path}: {e}")
    """
    pass


class DataValidationError(DataError):
    """Raised when data validation fails.

    Examples:
    - Missing required columns
    - Empty dataframe
    - Invalid data types
    - NaN/infinite values where not allowed
    - Shape mismatches

    Usage:
        >>> if df.empty:
        ...     raise DataValidationError("DataFrame is empty")
        >>> missing = set(required) - set(df.columns)
        >>> if missing:
        ...     raise DataValidationError(f"Missing columns: {missing}")
    """
    pass


class DataProcessingError(DataError):
    """Raised when data processing fails.

    Examples:
    - Feature engineering errors
    - Data transformation failures
    - Encoding/normalization errors
    - File saving failures

    Usage:
        >>> try:
        ...     df_processed = apply_transformations(df)
        ... except Exception as e:
        ...     raise DataProcessingError(f"Transformation failed: {e}")
    """
    pass
