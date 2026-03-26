"""Test DataFrame preparation with dummy targets for inference."""

import pandas as pd

from typing import List


def prepare_test_dataframe_with_dummy_targets(
    unique_df: pd.DataFrame,
    image_path_column: str,
    target_cols: List[str],
) -> pd.DataFrame:
    """
    Add dummy target columns (zeros) to unique image DataFrame for inference.

    Streaming datasets expect target_cols; for test inference we use zeros.

    Args:
        unique_df: DataFrame with one row per unique image (must include image_path_column).
        image_path_column: Column containing image paths.
        target_cols: Target column names to add with zero values.

    Returns:
        DataFrame with image_path_column and target_cols (all 0.0).
    """
    data = {image_path_column: unique_df[image_path_column]}
    n = len(unique_df)
    for col in target_cols:
        data[col] = [0.0] * n
    return pd.DataFrame(data)
