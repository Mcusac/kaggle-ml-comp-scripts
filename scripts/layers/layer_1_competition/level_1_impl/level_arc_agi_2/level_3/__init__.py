"""ARC level_3: composition tier (trainer registry, neural eval, submit/TTA dispatch)."""

from .llm_tta_runner import predict_attempts_for_llm_tta_dfs
from .neural_eval_score import score_neural_on_evaluation
from .submit_strategy_dispatch import predict_attempts_for_submit_strategy
from .trainer_registry import get_trainer, list_available_models

__all__ = [
    "get_trainer",
    "list_available_models",
    "predict_attempts_for_llm_tta_dfs",
    "predict_attempts_for_submit_strategy",
    "score_neural_on_evaluation",
]
