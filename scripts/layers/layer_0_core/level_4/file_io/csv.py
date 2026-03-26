"""CSV loading and basic tabular data I/O."""

import pandas as pd

from pathlib import Path
from typing import List, Optional, Union

from level_0 import get_logger, DataLoadError, DataValidationError, ensure_dir
from level_2 import validate_dataframe
from level_3 import validate_path_is_file

logger = get_logger(__name__)


def load_csv_raw(path: Union[str, Path], **kwargs) -> pd.DataFrame:
    """
    Load CSV without validation.
    
    Args:
        path: Path to CSV file
        **kwargs: Additional arguments passed to pd.read_csv()
        
    Returns:
        Loaded DataFrame
    """
    return pd.read_csv(Path(path), **kwargs)


def load_csv(
    path: Union[str, Path],
    *,
    required_cols: Optional[List[str]] = None,
    min_rows: int = 1,
    **kwargs,
) -> pd.DataFrame:
    """
    Load a single CSV file with validation.
    
    Args:
        path: Path to CSV file
        required_cols: List of required column names
        min_rows: Minimum number of rows required (default: 1)
        **kwargs: Additional arguments passed to pd.read_csv()
        
    Returns:
        Validated DataFrame
        
    Raises:
        DataValidationError: If path is invalid
        DataLoadError: If CSV cannot be read
        DataValidationError: If validation fails (missing columns, too few rows)
        
    Example:
        >>> df = load_csv('data.csv', required_cols=['id', 'value'], min_rows=10)
    """
    try:
        path_obj = validate_path_is_file(path, name="CSV file")
    except Exception as e:
        raise DataValidationError(f"Invalid CSV path: {e}")

    try:
        df = pd.read_csv(path_obj, **kwargs)
    except Exception as e:
        raise DataLoadError(f"Failed to load CSV {path_obj}: {e}")

    validate_dataframe(
        df,
        required_columns=required_cols,
        min_rows=min_rows,
        name="CSV",
    )

    logger.debug(
        f"Loaded CSV: {path_obj} "
        f"({len(df)} rows, {len(df.columns)} columns)"
    )
    return df


def save_csv(
    df: pd.DataFrame,
    path: Union[str, Path],
    *,
    index: bool = False,
    **kwargs,
) -> None:
    """
    Save a DataFrame to a CSV file.

    Args:
        df: DataFrame to save
        path: Path where to save CSV file
        index: Whether to include the index in the saved file
        **kwargs: Additional arguments passed to df.to_csv()

    Raises:
        DataValidationError: If save fails

    Example:
        >>> save_csv(df, 'data.csv')
    """
    path = Path(path)
    try:
        ensure_dir(path.parent)
        df.to_csv(path, index=index, **kwargs)
        logger.debug(f"Saved CSV: {path}")
    except Exception as e:
        raise DataValidationError(f"Failed to save CSV {path}: {e}")