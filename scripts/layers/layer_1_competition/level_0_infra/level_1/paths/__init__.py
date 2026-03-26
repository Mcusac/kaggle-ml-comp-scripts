"""Path resolution, Kaggle heuristics, and metadata path fallbacks."""

from .env_paths import (
    get_run_py_path,
    get_data_root_path,
    get_output_path,
    get_input_path,
    get_model_path,
    get_best_model_path,
    get_submission_path,
)
from .path_utils import (
    is_kaggle_input,
    resolve_data_root,
)

__all__ = [
    "get_run_py_path",
    "get_data_root_path",
    "get_output_path",
    "get_input_path",
    "get_model_path",
    "get_best_model_path",
    "get_submission_path",
    "is_kaggle_input",
    "resolve_data_root",
]
