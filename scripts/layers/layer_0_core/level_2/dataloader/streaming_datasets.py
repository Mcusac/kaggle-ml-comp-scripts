"""Streaming dataset factory for test inference."""

import pandas as pd

from typing import Callable, List, Union

from layers.layer_0_core.level_1 import StreamingDataset, StreamingSplitDataset


def create_streaming_dataset_for_test(
    data: pd.DataFrame,
    data_root: str,
    transform: Callable,
    target_cols: List[str],
    dataset_type: str,
    image_path_column: str = 'image_path',
) -> Union[StreamingDataset, StreamingSplitDataset]:
    """
    Create StreamingDataset or StreamingSplitDataset for test inference.

    Args:
        data: DataFrame with image_path_column and target_cols (dummy values ok).
        data_root: Root directory for image paths.
        transform: Transform applied to images.
        target_cols: Target column names (dummy zeros used for inference).
        dataset_type: 'full' for StreamingDataset, 'split' for StreamingSplitDataset.
        image_path_column: Column containing relative image paths.

    Returns:
        StreamingDataset or StreamingSplitDataset instance.

    Raises:
        ValueError: If dataset_type is not 'full' or 'split'.
    """
    if dataset_type not in ('full', 'split'):
        raise ValueError(f"dataset_type must be 'full' or 'split', got {dataset_type}")

    DatasetClass = StreamingSplitDataset if dataset_type == 'split' else StreamingDataset
    return DatasetClass(
        data,
        data_root=data_root,
        transform=transform,
        target_cols=target_cols,
        shuffle=False,
        image_path_column=image_path_column,
    )
