"""ARC level_2: training + inference utilities (no orchestration).

Conceptual subpackages (organised by purpose, not by dependency level):
- ``lm/``         — ARC LM backend config, ABC, factory, and concrete backends
- ``scoring/``    — teacher-forced NLL core + augmentation-aware scoring
- ``train/``      — TinyGridCNN training + LM token-budget trimming
- ``pipelines/``  — local-eval orchestrators (score submission, benchmark rankers)
"""

from .scoring import (
    aggregate_scores_across_augmentations,
    calc_scores,
    calc_scores_chunked,
    calc_scores_under_augmentations,
    concat_calc_score_batches,
    format_augmented_query_reply_batch,
    format_augmented_query_reply_strings,
    invert_candidate_grid,
)
from .lm import (
    ArcLmBackend,
    ArcLmBackendConfig,
    MockArcLmBackend,
    TransformersArcLmBackend,
    UnslothArcLmBackend,
    build_lm_backend,
)
from .inference import predict_grid_from_checkpoint
from .pipelines import (
    pipeline_run_benchmark_rankers_from_artifacts,
    pipeline_run_score_submission,
)
from .train import (
    run_grid_cnn_training,
    train_trim_task_train_pairs_to_token_budget,
)

__all__ = [
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
    "MockArcLmBackend",
    "UnslothArcLmBackend",
    "TransformersArcLmBackend",
    "build_lm_backend",
    "run_grid_cnn_training",
    "train_trim_task_train_pairs_to_token_budget",
]
