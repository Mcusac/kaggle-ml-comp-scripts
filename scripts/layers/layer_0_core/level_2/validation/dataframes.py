"""DataFrame validation.

Validation utilities for pandas DataFrames.
"""

import pandas as pd

from typing import Optional, List

from layers.layer_0_core.level_0 import DataValidationError
from layers.layer_0_core.level_1 import check_not_none, check_min_collection_length


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Optional[List[str]] = None,
    min_rows: int = 1,
    name: str = "DataFrame"
) -> None:
    """
    Validate DataFrame structure and content.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names. Validates that all
                         specified columns exist in the DataFrame
        min_rows: Minimum number of rows required (default: 1)
        name: Name of DataFrame for error messages
        
    Raises:
        DataValidationError: If validation fails for any reason:
            - DataFrame is None or empty
            - Row count is below minimum
            - Required columns are missing
            
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> validate_dataframe(df, required_columns=['a', 'b'], min_rows=2)
    """
    check_not_none(df, name)
    
    if df.empty:
        raise DataValidationError(f"{name} is empty")
    
    check_min_collection_length(df, min_rows, f"{name} rows")
    
    if required_columns:
        missing = set(required_columns) - set(df.columns)
        if missing:
            raise DataValidationError(
                f"{name} missing required columns: {sorted(missing)}. "
                f"Available columns: {sorted(df.columns.tolist())}"
            )


def validate_column_values(
    df: pd.DataFrame,
    column: str,
    check_null: bool = False,
    check_empty: bool = False,
    name: str = "DataFrame"
) -> None:
    """
    Validate values in a specific DataFrame column.
    
    Args:
        df: DataFrame containing the column
        column: Column name to validate
        check_null: If True, raise error if column contains null values
        check_empty: If True, raise error if column contains empty strings
        name: Name of DataFrame for error messages
        
    Raises:
        DataValidationError: If column is missing or contains invalid values
        
    Example:
        >>> validate_column_values(df, 'email', check_null=True, check_empty=True)
    """
    if column not in df.columns:
        raise DataValidationError(
            f"{name} missing required column '{column}'. "
            f"Available: {sorted(df.columns.tolist())}"
        )
    
    if check_null:
        null_mask = df[column].isnull()
        if null_mask.any():
            null_count = null_mask.sum()
            raise DataValidationError(
                f"{name} has {null_count} null values in '{column}' column"
            )
    
    if check_empty:
        empty_mask = df[column].astype(str).str.strip() == ''
        if empty_mask.any():
            empty_count = empty_mask.sum()
            raise DataValidationError(
                f"{name} has {empty_count} empty values in '{column}' column"
            )