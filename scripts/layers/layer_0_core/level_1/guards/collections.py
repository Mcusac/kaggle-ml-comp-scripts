"""Collection length guards."""

from typing import Sized

from level_0 import DataValidationError


def check_min_collection_length(
    collection: Sized,
    min_length: int,
    *,
    name: str = "collection",
) -> None:
    """
    Ensure collection has at least a minimum length.

    Args:
        collection: Object implementing __len__
        min_length: Required minimum length
        name: Name used in error message

    Raises:
        DataValidationError: If collection is too short
    """
    actual_length = len(collection)

    if actual_length < min_length:
        raise DataValidationError(
            f"{name} has {actual_length} elements; minimum {min_length} required"
        )