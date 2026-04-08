"""ARC level_2: training + inference utilities (no orchestration)."""

from .reference_ranking import (
    ENSEMBLE_REFERENCE_RANKERS,
    ensemble_hashable_grid,
    ensemble_score_full_probmul_3,
    ensemble_score_kgmon,
    ensemble_score_sum,
    reference_hashable_solution,
)
from .augmentation_scoring import (
    aggregate_scores_across_augmentations,
    calc_scores,
    calc_scores_chunked,
    calc_scores_under_augmentations,
    concat_calc_score_batches,
    format_augmented_query_reply_batch,
    format_augmented_query_reply_strings,
    invert_candidate_grid,
)
from .arc_lm_backend import (
    ArcLmBackend,
    ArcLmBackendConfig,
    UnslothArcLmBackend,
    TransformersArcLmBackend,
    build_lm_backend,
)
from .inference import predict_grid_from_checkpoint
from .pipeline_local_eval import (
    pipeline_run_benchmark_rankers_from_artifacts,
    pipeline_run_score_submission,
)
from .train import run_grid_cnn_training
from .train_cut_to_token_budget import train_trim_task_train_pairs_to_token_budget

__all__ = [
    "ENSEMBLE_REFERENCE_RANKERS",
    "ensemble_hashable_grid",
    "ensemble_score_full_probmul_3",
    "ensemble_score_kgmon",
    "ensemble_score_sum",
    "reference_hashable_solution",
    "aggregate_scores_across_augmentations",
    "calc_scores",
    "calc_scores_chunked",
    "calc_scores_under_augmentations",
    "concat_calc_score_batches",
    "format_augmented_query_reply_batch",
    "format_augmented_query_reply_strings",
    "invert_candidate_grid",
    "predict_grid_from_checkpoint",
    "pipeline_run_score_submission",
    "pipeline_run_benchmark_rankers_from_artifacts",
    "ArcLmBackendConfig",
    "ArcLmBackend",
    "UnslothArcLmBackend",
    "TransformersArcLmBackend",
    "build_lm_backend",
    "run_grid_cnn_training",
    "train_trim_task_train_pairs_to_token_budget",
]
