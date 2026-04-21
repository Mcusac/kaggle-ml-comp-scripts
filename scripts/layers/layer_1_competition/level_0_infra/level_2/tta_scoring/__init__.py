"""Test-time augmentation scoring patterns for LM contests."""

from .augmentation_scoring import (
    calc_scores_under_augmentations,
    format_augmented_query_reply_batch,
    format_augmented_query_reply_strings,
    invert_candidate_grid,
)

__all__ = [
    "calc_scores_under_augmentations",
    "format_augmented_query_reply_batch",
    "format_augmented_query_reply_strings",
    "invert_candidate_grid",
]
