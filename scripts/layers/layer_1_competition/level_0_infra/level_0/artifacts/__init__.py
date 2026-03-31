"""Artifact IO helpers shared across contest implementations.

This package is infra-only and must not import from `level_1_impl`.
"""

from .json_artifacts import read_json, write_json, write_json_atomic
from .best_config import load_best_config_json
from .pickle_artifacts import load_pickle_artifact, save_pickle_artifact
from .run_dirs import ensure_run_dir
from .schema import (
    ArtifactKeys,
    artifacts_merge,
    capture_config_paths,
    capture_metrics_paths,
    capture_model_paths,
    capture_submission_paths,
    metadata_merge,
)

__all__ = [
    "ArtifactKeys",
    "artifacts_merge",
    "capture_config_paths",
    "capture_metrics_paths",
    "capture_model_paths",
    "capture_submission_paths",
    "ensure_run_dir",
    "load_best_config_json",
    "load_pickle_artifact",
    "metadata_merge",
    "read_json",
    "save_pickle_artifact",
    "write_json",
    "write_json_atomic",
]

