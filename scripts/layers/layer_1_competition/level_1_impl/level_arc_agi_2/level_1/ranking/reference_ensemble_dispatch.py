"""Contest glue: reference ensemble ranker dispatch.

Requires contest ``ENSEMBLE_REFERENCE_RANKERS``; uses infra
``ensemble_predictions_to_guess_map`` to build the guess map consumed by those rankers.
"""

from __future__ import annotations

from layers.layer_1_competition.level_0_infra.level_1 import (
    CandidatePrediction,
    ensemble_predictions_to_guess_map,
)

from .ensemble_reference_rankers import ENSEMBLE_REFERENCE_RANKERS

Grid = list[list[int]]


def ensemble_rank_predictions_reference(
    predictions: list[CandidatePrediction],
    *,
    ranker: str,
) -> list[Grid]:
    key = str(ranker or "").strip().lower()
    if key not in ENSEMBLE_REFERENCE_RANKERS:
        raise ValueError(
            f"Unknown reference ranker {ranker!r}. Use: {sorted(ENSEMBLE_REFERENCE_RANKERS)}."
        )
    guesses = ensemble_predictions_to_guess_map(predictions)
    return ENSEMBLE_REFERENCE_RANKERS[key](guesses)
