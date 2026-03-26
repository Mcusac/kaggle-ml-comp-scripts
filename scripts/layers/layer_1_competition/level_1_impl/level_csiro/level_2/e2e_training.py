"""End-to-end training for train-and-export pipeline."""

from typing import Any, Dict, Optional

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import train_pipeline

logger = get_logger(__name__)


def train_end_to_end_model(
    data_root: str,
    model: Optional[str],
    variant_id: Optional[str],
    dataset_type: str,
) -> Dict[str, Any]:
    """Train end-to-end model."""
    logger.info("=" * 60)
    logger.info("End-to-End Training Mode")
    logger.info("=" * 60)

    logger.info("Starting end-to-end training...")
    avg_cv_score, fold_scores, _ = train_pipeline(
        data_root=data_root,
        model=model,
        dataset_type=dataset_type,
    )

    best_fold = max(range(len(fold_scores)), key=lambda i: fold_scores[i])
    best_fold_score = fold_scores[best_fold]

    logger.info("Best fold: %s (score: %.4f)", best_fold, best_fold_score)

    return {
        "variant_id": variant_id,
        "cv_score": avg_cv_score,
        "fold_scores": fold_scores,
        "best_fold": best_fold,
        "best_fold_score": best_fold_score,
        "model_name": model,
        "dataset_type": dataset_type,
    }
