"""ARC level_2: training + inference utilities (no orchestration)."""

from .inference import predict_grid_from_checkpoint
from .arc_lm_backend import ArcLmBackendConfig, ArcLmBackend, build_lm_backend
from .arc_lm_adaptation import ArcLmAdaptationConfig, run_task_adaptation
from .arc_lm_runtime import ArcLmRuntimeProfile, ArcLmBudget, apply_runtime_profile, build_budget
from .infer_time_deadline import (
    infer_epoch_now,
    infer_should_stop_by_end_time,
    infer_should_stop_inner_loop,
)
from .llm_tta_inference import LlmTtaDfsConfig
from .lm_notebook_env_hints import (
    NOTEBOOK_ENV_CUDA_VISIBLE_DEVICES,
    NOTEBOOK_ENV_KAGGLE_RERUN,
    NOTEBOOK_ENV_OMP_THREADS,
    NOTEBOOK_ENV_PYTORCH_ALLOCATOR,
    NOTEBOOK_ENV_TORCH_COMPILE_DISABLE,
    NOTEBOOK_ENV_TRITON_PTXAS,
    NOTEBOOK_ENV_UNSLOTH_COMPILED,
    NOTEBOOK_ENV_UNSLOTH_STATS,
)
from .train import run_grid_cnn_training
from .train_cut_to_token_budget import train_trim_task_train_pairs_to_token_budget

__all__ = [
    "predict_grid_from_checkpoint",
    "ArcLmBackendConfig",
    "ArcLmBackend",
    "build_lm_backend",
    "ArcLmRuntimeProfile",
    "ArcLmBudget",
    "apply_runtime_profile",
    "build_budget",
    "infer_epoch_now",
    "infer_should_stop_by_end_time",
    "infer_should_stop_inner_loop",
    "LlmTtaDfsConfig",
    "NOTEBOOK_ENV_CUDA_VISIBLE_DEVICES",
    "NOTEBOOK_ENV_KAGGLE_RERUN",
    "NOTEBOOK_ENV_OMP_THREADS",
    "NOTEBOOK_ENV_PYTORCH_ALLOCATOR",
    "NOTEBOOK_ENV_TORCH_COMPILE_DISABLE",
    "NOTEBOOK_ENV_TRITON_PTXAS",
    "NOTEBOOK_ENV_UNSLOTH_COMPILED",
    "NOTEBOOK_ENV_UNSLOTH_STATS",
    "run_grid_cnn_training",
    "train_trim_task_train_pairs_to_token_budget",
]
