"""Build (query, reply) strings under augmentations and score with infra NLL helpers."""

from collections.abc import Callable, Sequence
from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import (
    AggregateMode,
    aggregate_scores_across_augmentations,
    calc_scores,
    calc_scores_chunked,
)

Grid = list[list[int]]


def format_augmented_query_reply_strings(
    formatter: Any,
    input_grid: Grid,
    candidate_grid: Grid,
    spec: Any,
    *,
    apply_augmentation: Callable[[Grid, Any], Grid],
) -> tuple[str, str]:
    """Apply ``spec`` to both grids, then build chat query + reply strings for scoring."""
    aug_in = apply_augmentation(input_grid, spec)
    aug_out = apply_augmentation(candidate_grid, spec)
    q = formatter.fmt_query_from_input_grid(aug_in)
    a = formatter.fmt_reply_from_output_grid(aug_out)
    return q, a


def format_augmented_query_reply_batch(
    formatter: Any,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[Any],
    *,
    apply_augmentation: Callable[[Grid, Any], Grid],
) -> tuple[list[str], list[str]]:
    """Build parallel ``queries`` / ``answers`` lists for :func:`calc_scores`."""
    queries: list[str] = []
    answers: list[str] = []
    for spec in specs:
        q, a = format_augmented_query_reply_strings(
            formatter,
            input_grid,
            candidate_grid,
            spec,
            apply_augmentation=apply_augmentation,
        )
        queries.append(q)
        answers.append(a)
    return queries, answers


def invert_candidate_grid(
    grid: Grid,
    spec: Any,
    *,
    invert_augmentation: Callable[[Grid, Any], Grid],
) -> Grid:
    """Map a grid from augmented space back to the original layout."""
    return invert_augmentation(grid, spec)


def calc_scores_under_augmentations(
    model: Any,
    tokenizer: Any,
    formatter: Any,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[Any],
    *,
    apply_augmentation: Callable[[Grid, Any], Grid],
    pad_id: int | None = None,
    chunk_size: int | None = None,
    aggregate: AggregateMode = "none",
) -> list[float] | float:
    """Score ``candidate_grid`` under each augmentation in augmented prompt space."""
    queries, answers = format_augmented_query_reply_batch(
        formatter,
        input_grid,
        candidate_grid,
        specs,
        apply_augmentation=apply_augmentation,
    )
    if chunk_size is not None:
        nlls = calc_scores_chunked(queries, answers, tokenizer, model, chunk_size=int(chunk_size), pad_id=pad_id)
    else:
        nlls = calc_scores(queries, answers, tokenizer, model, pad_id=pad_id)
    if aggregate == "none":
        return nlls
    return aggregate_scores_across_augmentations(nlls, mode=aggregate)


__all__ = [
    "calc_scores_under_augmentations",
    "format_augmented_query_reply_batch",
    "format_augmented_query_reply_strings",
    "invert_candidate_grid",
]
