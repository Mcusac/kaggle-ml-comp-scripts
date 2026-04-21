"""ARC augmentation specs + infra TTA scoring (bound ``apply_augmentation`` / ``invert``)."""

from collections.abc import Sequence
from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import AggregateMode
from layers.layer_1_competition.level_0_infra.level_2.tta_scoring import augmentation_scoring as _tta

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ranking.augmentations import (
    AugmentationSpec,
    apply_augmentation,
    invert_augmentation,
)

Grid = list[list[int]]


def format_augmented_query_reply_strings(
    formatter: Any,
    input_grid: Grid,
    candidate_grid: Grid,
    spec: AugmentationSpec,
) -> tuple[str, str]:
    return _tta.format_augmented_query_reply_strings(
        formatter,
        input_grid,
        candidate_grid,
        spec,
        apply_augmentation=apply_augmentation,
    )


def format_augmented_query_reply_batch(
    formatter: Any,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[AugmentationSpec],
) -> tuple[list[str], list[str]]:
    return _tta.format_augmented_query_reply_batch(
        formatter,
        input_grid,
        candidate_grid,
        specs,
        apply_augmentation=apply_augmentation,
    )


def invert_candidate_grid(grid: Grid, spec: AugmentationSpec) -> Grid:
    return _tta.invert_candidate_grid(grid, spec, invert_augmentation=invert_augmentation)


def calc_scores_under_augmentations(
    model: Any,
    tokenizer: Any,
    formatter: Any,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[AugmentationSpec],
    *,
    pad_id: int | None = None,
    chunk_size: int | None = None,
    aggregate: AggregateMode = "none",
) -> list[float] | float:
    return _tta.calc_scores_under_augmentations(
        model,
        tokenizer,
        formatter,
        input_grid,
        candidate_grid,
        specs,
        apply_augmentation=apply_augmentation,
        pad_id=pad_id,
        chunk_size=chunk_size,
        aggregate=aggregate,
    )


__all__ = [
    "Grid",
    "calc_scores_under_augmentations",
    "format_augmented_query_reply_batch",
    "format_augmented_query_reply_strings",
    "invert_candidate_grid",
]
