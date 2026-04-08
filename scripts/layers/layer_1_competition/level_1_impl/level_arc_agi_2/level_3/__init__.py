"""ARC level_3: composition tier (trainer registry, neural eval, LLM-TTA runner)."""

from .llm_tta_runner import predict_attempts_for_llm_tta_dfs
from .neural_eval_score import score_neural_on_evaluation
from .trainer_registry import get_trainer, list_available_models

__all__ = [
    "get_trainer",
    "list_available_models",
    "predict_attempts_for_llm_tta_dfs",
    "score_neural_on_evaluation",
]
