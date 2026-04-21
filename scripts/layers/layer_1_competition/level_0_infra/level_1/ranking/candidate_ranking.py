"""Merge and rank candidate grids using model scores + augmentation consistency."""

from collections import defaultdict
from dataclasses import dataclass

from layers.layer_1_competition.level_0_infra.level_0 import grid_int_hash_key

Grid = list[list[int]]


@dataclass(frozen=True)
class CandidatePrediction:
    """Single candidate emitted by one augmentation branch."""

    grid: Grid
    model_score: float
    aug_key: str = ""
    aug_likelihood_score: float = 0.0


@dataclass(frozen=True)
class RankedCandidate:
    """Merged candidate score used for final selection."""

    grid: Grid
    combined_score: float
    support_count: int
    mean_model_score: float
    mean_aug_likelihood_score: float


def rank_candidate_grids(
    predictions: list[CandidatePrediction],
    *,
    consistency_weight: float = 1.0,
    model_weight: float = 1.0,
    augmentation_likelihood_weight: float = 1.0,
) -> list[RankedCandidate]:
    """Merge duplicate grids and rank by weighted score."""
    grouped: dict[tuple[tuple[int, ...], ...], list[CandidatePrediction]] = defaultdict(list)
    for pred in predictions:
        grouped[grid_int_hash_key(pred.grid)].append(pred)

    ranked: list[RankedCandidate] = []
    for key, items in grouped.items():
        support = len(items)
        mean_model = sum(float(i.model_score) for i in items) / float(support)
        mean_aug_likelihood = sum(float(i.aug_likelihood_score) for i in items) / float(support)
        combined = (
            float(consistency_weight) * float(support)
            + float(model_weight) * float(mean_model)
            + float(augmentation_likelihood_weight) * float(mean_aug_likelihood)
        )
        ranked.append(
            RankedCandidate(
                grid=[list(row) for row in key],
                combined_score=float(combined),
                support_count=int(support),
                mean_model_score=float(mean_model),
                mean_aug_likelihood_score=float(mean_aug_likelihood),
            )
        )
    ranked.sort(
        key=lambda item: (
            item.combined_score,
            item.support_count,
            item.mean_aug_likelihood_score,
            item.mean_model_score,
        ),
        reverse=True,
    )
    return ranked


__all__ = [
    "CandidatePrediction",
    "Grid",
    "RankedCandidate",
    "rank_candidate_grids",
]
