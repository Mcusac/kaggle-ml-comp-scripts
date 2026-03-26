"""Load and validate test CSV data for inference."""

import pandas as pd

from pathlib import Path
from typing import Union

from layers.layer_0_core.level_0 import get_logger
from level_3 import validate_path_is_file
from level_4 import load_csv

logger = get_logger(__name__)


def load_and_validate_test_data(
    test_csv_path: Union[str, Path],
    image_path_column: str = 'image_path',
) -> pd.DataFrame:
    """
    Load test CSV and return one row per unique image.

    Generic version: any test CSV with multiple rows per image (e.g. one per target)
    can be reduced to unique images for inference/feature extraction.

    Args:
        test_csv_path: Path to test.csv.
        image_path_column: Column containing image paths (from contest data_schema).

    Returns:
        DataFrame with one row per unique image (subset of columns including
        image_path_column).

    Raises:
        ValueError: If empty, missing image_path_column, or no unique images.
        FileNotFoundError: If test_csv_path does not exist.
    """
    df = load_csv(validate_path_is_file(test_csv_path, name="test.csv"), required_cols=[image_path_column])

    if len(df) == 0:
        raise ValueError(f"test.csv is empty: {test_csv_path}")

    unique = df[[image_path_column]].drop_duplicates().reset_index(drop=True)
    if len(unique) == 0:
        raise ValueError("No unique images found in test.csv")

    return unique
