"""ARC level_1: contest-local orchestration support utilities.

Level 1 holds shared helpers for contest stages (level_2), orchestration (level_3),
and handlers (e.g., run tracking, PipelineResult).
"""

from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult
from .model import TinyGridCNN
from .augmentations import (
    AugmentationSpec,
    IDENTITY_AUGMENTATION,
    apply_augmentation,
    generate_augmentation_specs,
    invert_augmentation,
)
from .candidate_scoring import CandidatePrediction, RankedCandidate, rank_candidate_grids
from .decoder_dfs import GridCandidate, decode_grid_candidates
from .token_decoder import TokenDecodeCandidate, decode_tokens_to_grids
from .lm_qwen_chat_format import ArcQwenGridChatFormatter, arc_count_tokens
from .scoring import (
    rank_heuristics_on_training,
    score_heuristic_on_evaluation,
    score_heuristic_on_training_challenges,
    select_best_heuristic,
    select_best_heuristic_on_training,
)
from .submission_two_attempt_build import (
    submission_empty_shell_for_challenges,
    submission_fill_test_attempts,
)
from .tuning_io import load_chosen_params_from_tuned_config
from .run_tracking import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    init_run_context,
    update_run_metadata,
)

__all__ = [
    "PipelineResult",
    "RunContext",
    "TinyGridCNN",
    "AugmentationSpec",
    "IDENTITY_AUGMENTATION",
    "apply_augmentation",
    "generate_augmentation_specs",
    "invert_augmentation",
    "CandidatePrediction",
    "RankedCandidate",
    "rank_candidate_grids",
    "GridCandidate",
    "decode_grid_candidates",
    "TokenDecodeCandidate",
    "decode_tokens_to_grids",
    "ArcQwenGridChatFormatter",
    "arc_count_tokens",
    "rank_heuristics_on_training",
    "score_heuristic_on_evaluation",
    "score_heuristic_on_training_challenges",
    "select_best_heuristic",
    "select_best_heuristic_on_training",
    "submission_empty_shell_for_challenges",
    "submission_fill_test_attempts",
    "load_chosen_params_from_tuned_config",
    "copy_artifact_into_run",
    "finalize_run_failure",
    "finalize_run_success",
    "init_run_context",
    "update_run_metadata",
]
