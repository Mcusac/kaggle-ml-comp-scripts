"""Map :class:`CandidatePrediction` rows to notebook-style guess dicts."""

from __future__ import annotations

from typing import Any

from .candidate_ranking import CandidatePrediction


def ensemble_candidate_to_guess_dict(pred: CandidatePrediction) -> dict[str, Any]:
    """Single guess entry: ``beam_score`` uses ``-model_score`` as NLL-ish alignment."""
    return {
        "solution": [list(row) for row in pred.grid],
        "beam_score": float(-pred.model_score),
        "score_aug": [float(pred.aug_likelihood_score)],
    }


def ensemble_predictions_to_guess_map(
    predictions: list[CandidatePrediction],
) -> dict[str, dict[str, Any]]:
    """Indexed keys for reference ensemble rankers (e.g. ``ensemble_score_sum``)."""
    return {str(i): ensemble_candidate_to_guess_dict(p) for i, p in enumerate(predictions)}