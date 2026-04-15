"""Runtime-level utilities.

- Hardware detection (device, CUDA status)
- Environment detection (Kaggle vs local)
- Subprocess execution (command runners)
- Reproducibility control (seeding)
- Memory statistics (GPU memory usage)

Core modules (device, process, seed, paths) do not log. The cuda subpackage
(recovery, monitoring, gpu_cleanup) may log for OOM recovery, GPU status, and
cleanup; callers may also log as appropriate to their layer.

Consumers needing is_kaggle, get_torch, or is_torch_available must import from layers.layer_0_core.level_0.
"""

from . import config, cuda

from .config import *
from .cuda import *

from .base_pipeline import BasePipeline
from .chunked_prediction import predict_in_chunks, predict_proteins_in_chunks
from .device import is_cuda_available, get_device_info, get_device
from .lazy_imports import lazy_import
from .metadata_paths import find_metadata_candidates
from .notebook_runner import safe_execute_cell
from .paths import (
    get_environment_type, 
    get_environment_paths, 
    get_environment_root, 
    get_default_submission_csv_path,
    get_kaggle_working_submission_csv_path,
    resolve_environment_path, 
    resolve_path
)
from .process import run_command
from .progress_config import ProgressVerbosity, ProgressConfig
from .seed import set_seed



__all__ = (
    list(config.__all__)
    + list(cuda.__all__)
    + [
    "BasePipeline",
    "predict_in_chunks",
    "predict_proteins_in_chunks",
    "is_cuda_available",
    "get_device_info",
    "get_device",
    "lazy_import",
    "find_metadata_candidates",
    "safe_execute_cell",
    "get_environment_type",
    "get_environment_paths",
    "get_environment_root",
    "get_default_submission_csv_path",
    "get_kaggle_working_submission_csv_path",
    "resolve_environment_path",
    "resolve_path",
    "run_command",
    "ProgressVerbosity",
    "ProgressConfig",
    "set_seed",
    ]
)
