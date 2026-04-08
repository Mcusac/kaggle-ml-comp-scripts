"""ARC-AGI-2 level_1: utilities that depend on infra or external tooling."""

from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult

from .eval_ranker_benchmark import (
    eval_benchmark_rankers,
    eval_run_selection_on_decoded,
    eval_safe_mean_max,
    eval_summarize_correct_beam_stats,
)
from .ensemble_prediction_bridge import ensemble_rank_predictions_reference
from .eval_submission_scoring import (
    eval_count_tasks,
    eval_score_submission_two_attempts,
)
from .eval_teacher_forced_score import (
    eval_teacher_forced_neg_sum_logprob,
    eval_teacher_forced_neg_sum_logprob_batch,
)
from .lm_qwen_chat_format import ArcQwenGridChatFormatter, arc_count_tokens
from .model import TinyGridCNN
from .run_tracking import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    init_run_context,
    update_run_metadata,
)
from .scoring import (
    rank_heuristics_on_training,
    score_heuristic_on_evaluation,
    score_heuristic_on_training_challenges,
    select_best_heuristic,
    select_best_heuristic_on_training,
)

__all__ = [
    "PipelineResult",
    "RunContext",
    "TinyGridCNN",
    "ArcQwenGridChatFormatter",
    "arc_count_tokens",
    "rank_heuristics_on_training",
    "score_heuristic_on_evaluation",
    "score_heuristic_on_training_challenges",
    "select_best_heuristic",
    "select_best_heuristic_on_training",
    "eval_teacher_forced_neg_sum_logprob",
    "eval_teacher_forced_neg_sum_logprob_batch",
    "eval_score_submission_two_attempts",
    "eval_count_tasks",
    "eval_run_selection_on_decoded",
    "eval_benchmark_rankers",
    "eval_summarize_correct_beam_stats",
    "eval_safe_mean_max",
    "ensemble_rank_predictions_reference",
    "copy_artifact_into_run",
    "finalize_run_failure",
    "finalize_run_success",
    "init_run_context",
    "update_run_metadata",
]
