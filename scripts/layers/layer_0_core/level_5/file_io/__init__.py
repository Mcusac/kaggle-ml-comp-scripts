"""Merge utilities (level_5) — imports from level_4 to avoid same-level imports."""

from .merge import (
    merge_json_from_input_and_working,
    merge_list_by_key_add_only,
    merge_list_by_key_working_replaces,
)

__all__ = [
    "merge_json_from_input_and_working",
    "merge_list_by_key_add_only",
    "merge_list_by_key_working_replaces",
]
