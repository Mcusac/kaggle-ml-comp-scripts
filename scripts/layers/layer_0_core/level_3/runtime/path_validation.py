"""Path validation.

Validation utilities for file paths and image paths.
"""

import pandas as pd

from pathlib import Path
from typing import Union, List

from layers.layer_0_core.level_0 import DataValidationError
from level_2 import validate_dataframe, validate_column_values

def validate_file_exists(
    path: Union[str, Path],
    name: str = "file"
) -> Path:
    """
    Validate that a file path exists.
    
    Args:
        path: Path to validate
        name: Description of the file for error messages
        
    Returns:
        Path object (for convenience in chaining)
        
    Raises:
        DataValidationError: If path is None or empty
        FileNotFoundError: If file doesn't exist
        
    Example:
        >>> path = validate_file_exists("data.csv", "input data")
        >>> # Use path...
    """
    if path is None:
        raise DataValidationError(f"{name} path cannot be None")
    
    if isinstance(path, str) and not path.strip():
        raise DataValidationError(f"{name} path cannot be empty string")
    
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"{name} not found: {path_obj}")
    
    return path_obj


def validate_path_is_file(
    path: Union[str, Path],
    name: str = "file"
) -> Path:
    """
    Validate that a path exists and is a file (not a directory).
    
    Args:
        path: Path to validate
        name: Description of the file for error messages
        
    Returns:
        Path object
        
    Raises:
        DataValidationError: If path is empty or not a file
        FileNotFoundError: If path doesn't exist
        
    Example:
        >>> config_path = validate_path_is_file("config.yaml", "configuration")
    """
    if not path:
        raise DataValidationError(f"{name} path cannot be empty")
    
    path_obj = validate_file_exists(path, name)
    
    if not path_obj.is_file():
        raise DataValidationError(f"{name} is not a file: {path_obj}")
    
    return path_obj


def validate_image_path(
    path: Union[str, Path],
    check_exists: bool = True,
    name: str = "image"
) -> Path:
    """
    Validate image path.
    
    Args:
        path: Path to validate
        check_exists: Whether to check if file exists (default: True)
        name: Description for error messages
        
    Returns:
        Path object
        
    Raises:
        DataValidationError: If path is invalid or not a file
        FileNotFoundError: If check_exists=True and file doesn't exist
        
    Example:
        >>> img_path = validate_image_path("photo.jpg")
        >>> # Don't check existence (e.g., for paths that will be created)
        >>> output_path = validate_image_path("output.png", check_exists=False)
    """
    if not path:
        raise DataValidationError(f"{name} path cannot be empty")
    
    path_obj = Path(path)
    
    if check_exists:
        if not path_obj.exists():
            raise FileNotFoundError(f"{name} not found: {path}")
        
        if not path_obj.is_file():
            raise DataValidationError(f"{name} is not a file: {path}")
    
    return path_obj


def validate_image_paths_in_dataframe(
    df: pd.DataFrame,
    image_column: str = 'image_path',
    check_exists: bool = False,
    max_missing_to_show: int = 10,
    name: str = "DataFrame"
) -> None:
    """
    Validate image paths in DataFrame column.
    
    Args:
        df: DataFrame containing image paths
        image_column: Name of column containing image paths
        check_exists: Whether to check if each file exists (can be slow for large datasets)
        max_missing_to_show: Maximum number of missing files to display in error
        name: Name of DataFrame for error messages
        
    Raises:
        DataValidationError: If image_column is missing or contains invalid paths
        FileNotFoundError: If check_exists=True and any files don't exist
        
    Example:
        >>> validate_image_paths_in_dataframe(
        ...     train_df, 
        ...     image_column='path',
        ...     check_exists=True,
        ...     name="training data"
        ... )
    """
    # Validate DataFrame structure
    validate_dataframe(df, required_columns=[image_column], name=name)
    
    # Check for null/empty paths
    validate_column_values(
        df, 
        image_column, 
        check_null=True, 
        check_empty=True, 
        name=name
    )
    
    # Optionally check if files exist
    if check_exists:
        missing_files: List[tuple] = []
        
        for idx, path in enumerate(df[image_column]):
            path_obj = Path(path)
            if not path_obj.exists():
                missing_files.append((idx, path))
                if len(missing_files) >= max_missing_to_show:
                    break
        
        if missing_files:
            missing_list = '\n'.join(
                [f"  Row {idx}: {path}" for idx, path in missing_files]
            )
            more_msg = f"\n  ... and possibly more" if len(missing_files) >= max_missing_to_show else ""
            
            raise FileNotFoundError(
                f"{name} contains missing image files:\n{missing_list}{more_msg}"
            )