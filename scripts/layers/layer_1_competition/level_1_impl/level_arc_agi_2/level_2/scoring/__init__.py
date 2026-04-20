"""ARC scoring subpackage: teacher-forced NLL core + augmentation-aware scoring."""

from .augmentation_scoring import (
    calc_scores_under_augmentations,
    format_augmented_query_reply_batch,
    format_augmented_query_reply_strings,
    invert_candidate_grid,
)
from .nll_core import (
    aggregate_scores_across_augmentations,
    calc_scores,
    calc_scores_chunked,
    concat_calc_score_batches,
)

__all__ = [
    "aggregate_scores_across_augmentations",
    "calc_scores",
    "calc_scores_chunked",
    "calc_scores_under_augmentations",
    "concat_calc_score_batches",
    "format_augmented_query_reply_batch",
    "format_augmented_query_reply_strings",
    "invert_candidate_grid",
]
