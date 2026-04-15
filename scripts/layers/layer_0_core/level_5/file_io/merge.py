"""Generic merge utilities for input + working directory patterns."""

from pathlib import Path
from typing import Any, Callable, List, Optional

from layers.layer_0_core.level_4 import load_json


def merge_list_by_key_add_only(
    input_items: List[Any],
    working_items: List[Any],
    key_fn: Callable[[Any], Any],
) -> List[Any]:
    """
    Merge lists: add working items whose key is not already in input.

    Args:
        input_items: Items from input (read-only source).
        working_items: Items from working (writable source).
        key_fn: Function to extract key from each item (e.g. lambda x: x.get('variant_id')).

    Returns:
        Merged list: input_items + working items whose key not in input.
    """
    result = list(input_items)
    existing_keys = {key_fn(item) for item in result}
    for item in working_items:
        if key_fn(item) not in existing_keys:
            result.append(item)
            existing_keys.add(key_fn(item))
    return result


def merge_list_by_key_working_replaces(
    input_items: List[Any],
    working_items: List[Any],
    key_fn: Callable[[Any], Any],
) -> List[Any]:
    """
    Merge lists: working replaces input for same key.

    For each working item, if its key exists in input, remove the input entry
    and append the working item; otherwise append the working item.

    Args:
        input_items: Items from input (read-only source).
        working_items: Items from working (writable source).
        key_fn: Function to extract key from each item (e.g. lambda x: (x.get('variant_id'), x.get('feature_filename'))).

    Returns:
        Merged list with working taking precedence for duplicates.
    """
    result = list(input_items)
    for item in working_items:
        key = key_fn(item)
        result = [r for r in result if key_fn(r) != key]
        result.append(item)
    return result


def merge_json_from_input_and_working(
    input_path: Optional[Path],
    working_path: Path,
    merge_fn: Callable[[List[Any], List[Any]], List[Any]],
    expected_type: type = list,
    file_type: str = "JSON",
) -> List[Any]:
    """
    Load JSON from input and working paths, merge with working taking precedence.

    Args:
        input_path: Read-only input file (e.g. /kaggle/input/...). None if local.
        working_path: Writable working file.
        merge_fn: (input_items, working_items) -> merged_items. Working overrides.
        expected_type: Expected JSON root type (list or dict).
        file_type: Label for error messages.

    Returns:
        Merged list.
    """
    input_items: List[Any] = []
    if input_path and input_path.exists():
        raw = load_json(
            input_path, expected_type=expected_type, file_type=file_type
        )
        input_items = raw if isinstance(raw, list) else ([raw] if raw is not None else [])

    working_items: List[Any] = []
    if working_path.exists():
        raw = load_json(
            working_path, expected_type=expected_type, file_type=file_type
        )
        working_items = raw if isinstance(raw, list) else ([raw] if raw is not None else [])

    return merge_fn(input_items, working_items)
