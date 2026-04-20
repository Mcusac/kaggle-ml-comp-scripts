"""ARC-AGI-2 level_1: utilities that depend on infra or external tooling.

Conceptual subpackages (organised by purpose, not by dependency level):
- ``cli/``     — argv builders (``commands/``), argparse registrars (``parsers/`` + ``extend_subparsers.py``) for ``run.py``
- ``lm/``      — Qwen chat formatting, completion-only collator, worker config
- ``eval/``    — submission scoring, ranker benchmarking
- ``scoring/`` — heuristic scoring on training/evaluation corpora
- ``run/``     — run-id / run-dir / run-metadata lifecycle helpers

The public surface below is preserved from the previous flat layout with
Run 12 removing broken re-exports (``eval_teacher_forced_*`` now imported
directly from ``level_0`` by consumers; ``rank_heuristics_on_training`` /
``select_best_heuristic*`` / ``rank_top_heuristics_for_submit`` were never
implemented and have been dropped along with their unreachable call sites).
"""

from .ensemble_prediction_bridge import ensemble_rank_predictions_reference
from .eval.ranker_benchmark import (
    eval_benchmark_rankers,
    eval_run_selection_on_decoded,
    eval_safe_mean_max,
    eval_summarize_correct_beam_stats,
)
from .eval.submission_scoring import eval_score_submission_two_attempts
from .lm.chat_format import ArcQwenGridChatFormatter, arc_count_tokens
from .lm.collator import QwenDataCollatorForCompletionOnlyLM
from .model import TinyGridCNN
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.run.finalize import (
    commit_run_artifacts,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.run.run_context import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    init_run_context,
    update_run_metadata,
)
from .scoring.grid_metrics import (
    eval_solution_grids_for_task,
    score_grid_exact_match,
)
from .scoring.heuristic_scoring import (
    score_heuristic_exact_match_on_training,
    score_heuristic_on_evaluation,
    score_heuristic_on_training_challenges,
)

__all__ = [
    "RunContext",
    "TinyGridCNN",
    "ArcQwenGridChatFormatter",
    "arc_count_tokens",
    "QwenDataCollatorForCompletionOnlyLM",
    "score_heuristic_on_evaluation",
    "score_heuristic_on_training_challenges",
    "eval_solution_grids_for_task",
    "score_grid_exact_match",
    "score_heuristic_exact_match_on_training",
    "eval_score_submission_two_attempts",
    "eval_run_selection_on_decoded",
    "eval_benchmark_rankers",
    "eval_summarize_correct_beam_stats",
    "eval_safe_mean_max",
    "ensemble_rank_predictions_reference",
    "commit_run_artifacts",
    "copy_artifact_into_run",
    "finalize_run_failure",
    "finalize_run_success",
    "init_run_context",
    "update_run_metadata",
]
