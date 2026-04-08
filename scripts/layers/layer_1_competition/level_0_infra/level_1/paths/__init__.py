"""Path resolution, Kaggle heuristics, and metadata path fallbacks."""

from layers.layer_0_core.level_0 import is_kaggle_input

from .env_paths import (
    get_run_py_path,
    get_data_root_path,
)
from .models import contest_models_dir, contest_model_dir
from .output_roots import contest_output_root
from .path_utils import resolve_data_root
from .runs import contest_runs_root, contest_run_dir
from .submissions import contest_submission_path

__all__ = [
    "get_run_py_path",
    "get_data_root_path",
    "contest_models_dir",
    "contest_model_dir",
    "contest_output_root",
    "is_kaggle_input",
    "resolve_data_root",
    "contest_runs_root",
    "contest_run_dir",
    "contest_submission_path",

]
