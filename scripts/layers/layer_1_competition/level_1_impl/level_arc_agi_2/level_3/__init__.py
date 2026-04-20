"""ARC level_3: composition tier (trainer registry, neural eval, LLM-TTA runner).

Subpackages (by purpose):
- ``trainer_registry/``     - ``NamedRegistry`` for training routines
- ``neural_eval_score/``    - evaluation exact-match scoring vs held-out solutions
- ``lm_peft_adapter/``      - lazy ``peft`` bindings for Unsloth / LoRA backends
- ``llm_tta_runner/``       - LLM-TTA DFS orchestrator + decode branches + artifacts + ranking
- ``lm_task_adaptation/``   - per-task Unsloth LoRA adaptation (row building + trainer runner)

Public exports from this package: ``get_trainer``, ``list_available_models``,
``predict_attempts_for_llm_tta_dfs``, ``score_neural_on_evaluation``.
"""

from .llm_tta_runner import predict_attempts_for_llm_tta_dfs
from .neural_eval_score import score_neural_on_evaluation
from .trainer_registry import get_trainer, list_available_models

__all__ = [
    "get_trainer",
    "list_available_models",
    "predict_attempts_for_llm_tta_dfs",
    "score_neural_on_evaluation",
]
