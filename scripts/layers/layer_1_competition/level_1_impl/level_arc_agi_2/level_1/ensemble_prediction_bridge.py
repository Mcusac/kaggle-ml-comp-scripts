"""Bridge :class:`CandidatePrediction` to notebook-shaped guess dicts (level_2; imports level_1 only)."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    CandidatePrediction,
    ENSEMBLE_REFERENCE_RANKERS,
    Grid,
)


def ensemble_candidate_to_guess_dict(pred: CandidatePrediction) -> dict[str, Any]:
    """Single guess entry: ``beam_score`` uses ``-model_score`` as NLL-ish alignment."""
    return {
        "solution": [list(row) for row in pred.grid],
        "beam_score": float(-pred.model_score),
        "score_aug": [float(pred.aug_likelihood_score)],
    }


def ensemble_predictions_to_guess_map(predictions: list[CandidatePrediction]) -> dict[str, dict[str, Any]]:
    """Indexed keys for :func:`ensemble_score_sum`."""
    return {str(i): ensemble_candidate_to_guess_dict(p) for i, p in enumerate(predictions)}


def ensemble_rank_predictions_reference(
    predictions: list[CandidatePrediction],
    *,
    ranker: str,
) -> list[Grid]:
    """Apply ``kgmon`` or ``probmul`` reference ranker; return ordered grids."""
    key = str(ranker or "").strip().lower()
    if key not in ENSEMBLE_REFERENCE_RANKERS:
        raise ValueError(
            f"Unknown reference ranker {ranker!r}. Use: {sorted(ENSEMBLE_REFERENCE_RANKERS)}."
        )
    guesses = ensemble_predictions_to_guess_map(predictions)
    return ENSEMBLE_REFERENCE_RANKERS[key](guesses)
