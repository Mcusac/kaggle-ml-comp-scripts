"""Pair (query, reply) strings under :class:`AugmentationSpec` and score them.

Uses the same forward/inverse grid transforms as TTA decoding, then delegates
scoring to :mod:`.nll_core`.
"""

from collections.abc import Sequence
from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    AugmentationSpec,
    apply_augmentation,
    invert_augmentation,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import ArcQwenGridChatFormatter

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    AggregateMode,
    aggregate_scores_across_augmentations,
    calc_scores,
    calc_scores_chunked,
)

Grid = list[list[int]]


def format_augmented_query_reply_strings(
    formatter: ArcQwenGridChatFormatter,
    input_grid: Grid,
    candidate_grid: Grid,
    spec: AugmentationSpec,
) -> tuple[str, str]:
    """Apply ``spec`` to both grids, then build Qwen chat query + reply strings for scoring."""
    aug_in = apply_augmentation(input_grid, spec)
    aug_out = apply_augmentation(candidate_grid, spec)
    q = formatter.fmt_query_from_input_grid(aug_in)
    a = formatter.fmt_reply_from_output_grid(aug_out)
    return q, a


def format_augmented_query_reply_batch(
    formatter: ArcQwenGridChatFormatter,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[AugmentationSpec],
) -> tuple[list[str], list[str]]:
    """Build parallel ``queries`` / ``answers`` lists for :func:`calc_scores`."""
    queries: list[str] = []
    answers: list[str] = []
    for spec in specs:
        q, a = format_augmented_query_reply_strings(formatter, input_grid, candidate_grid, spec)
        queries.append(q)
        answers.append(a)
    return queries, answers


def invert_candidate_grid(grid: Grid, spec: AugmentationSpec) -> Grid:
    """Map a grid from augmented space back to the original layout (thin wrapper over :func:`invert_augmentation`)."""
    return invert_augmentation(grid, spec)


def calc_scores_under_augmentations(
    model: Any,
    tokenizer: Any,
    formatter: ArcQwenGridChatFormatter,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[AugmentationSpec],
    *,
    pad_id: int | None = None,
    chunk_size: int | None = None,
    aggregate: AggregateMode = "none",
) -> list[float] | float:
    """Score ``candidate_grid`` under each augmentation in **augmented** prompt space (reference TTA pattern).

    Returns one NLL per spec, or a single aggregated value when ``aggregate`` is not ``none``.
    """
    queries, answers = format_augmented_query_reply_batch(formatter, input_grid, candidate_grid, specs)
    if chunk_size is not None:
        nlls = calc_scores_chunked(queries, answers, tokenizer, model, chunk_size=int(chunk_size), pad_id=pad_id)
    else:
        nlls = calc_scores(queries, answers, tokenizer, model, pad_id=pad_id)
    if aggregate == "none":
        return nlls
    return aggregate_scores_across_augmentations(nlls, mode=aggregate)
