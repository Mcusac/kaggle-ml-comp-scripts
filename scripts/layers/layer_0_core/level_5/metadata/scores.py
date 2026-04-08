"""Score extraction helpers for model export metadata."""

from pathlib import Path
from typing import Optional

from level_0 import get_logger
from level_4 import load_json_raw

logger = get_logger(__name__)


def extract_scores_from_json(
    *,
    model_path: Path,
    json_filename: str,
    best_fold: Optional[int],
) -> tuple[float, list, Optional[int]]:
    """Extract CV/fold scores from a model-adjacent metadata JSON file."""
    metadata_path = model_path.parent / json_filename
    cv_score = 0.0
    fold_scores = []
    extracted_best_fold = best_fold
    if metadata_path.exists():
        try:
            info = load_json_raw(metadata_path)
            cv_score = info.get("cv_score", 0.0)
            fold_scores = info.get("fold_scores", [])
            extracted_best_fold = info.get("best_fold", best_fold)
        except Exception as e:
            logger.warning(f"Could not load {json_filename}: {e}")
    return cv_score, fold_scores, extracted_best_fold


def resolve_best_fold_and_score(
    *,
    best_fold: Optional[int],
    extracted_best_fold: Optional[int],
    fold_scores: list,
    cv_score: float,
) -> tuple[Optional[int], float]:
    """Resolve best fold index and score from fold data with cv fallback."""
    best_fold_used = best_fold if best_fold is not None else extracted_best_fold
    best_fold_score = (
        fold_scores[best_fold_used] if best_fold_used is not None and best_fold_used < len(fold_scores) else cv_score
    )
    return best_fold_used, best_fold_score


