"""Suggested process environment keys for reference-notebook parity (documentation constants only).

Full Unsloth multi-GPU orchestration belongs in notebooks or infra; this module is additive metadata.
# CANDIDATE: move to level_0_infra — central env matrix for Kaggle kernels.
"""

from __future__ import annotations

# Names only (values are set in shell / notebook).
NOTEBOOK_ENV_CUDA_VISIBLE_DEVICES = "CUDA_VISIBLE_DEVICES"
NOTEBOOK_ENV_KAGGLE_RERUN = "KAGGLE_IS_COMPETITION_RERUN"
NOTEBOOK_ENV_TORCH_COMPILE_DISABLE = "TORCH_COMPILE_DISABLE"
NOTEBOOK_ENV_UNSLOTH_COMPILED = "UNSLOTH_USE_COMPILED"
NOTEBOOK_ENV_UNSLOTH_STATS = "UNSLOTH_DISABLE_STATISTICS"
NOTEBOOK_ENV_TRITON_PTXAS = "TRITON_PTXAS_PATH"
NOTEBOOK_ENV_OMP_THREADS = "OMP_NUM_THREADS"
NOTEBOOK_ENV_PYTORCH_ALLOCATOR = "PYTORCH_CUDA_ALLOC_CONF"
