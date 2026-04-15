"""Streaming test DataLoader from CSV path (distinct from layers.layer_0_core.level_4 DataFrame-based factory)."""

from typing import List, Tuple

from layers.layer_0_core.level_2 import (
    build_preprocessing_transforms,
    create_dataloader_from_dataset,
    create_streaming_dataset_for_test,
)
from layers.layer_0_core.level_5 import load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets


def create_streaming_test_dataloader(
    test_csv_path: str,
    data_root: str,
    image_path_column: str,
    primary_targets: List[str],
    image_size: Tuple[int, int],
    batch_size: int = 32,
    dataset_type: str = "split",
    num_workers: int = 0,
):
    """
    Create DataLoader for test set (unique images, dummy targets).

    Uses streaming datasets and level_2 preprocessing transforms.
    """
    unique = load_and_validate_test_data(test_csv_path, image_path_column=image_path_column)
    test_data = prepare_test_dataframe_with_dummy_targets(
        unique, image_path_column, primary_targets
    )
    transform = build_preprocessing_transforms(image_size)
    ds = create_streaming_dataset_for_test(
        test_data,
        data_root=data_root,
        transform=transform,
        target_cols=primary_targets,
        dataset_type=dataset_type,
        image_path_column=image_path_column,
    )
    return create_dataloader_from_dataset(
        ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=False,
    )
