"""Shared artifact/metadata key conventions for PipelineResult capture.

This does not change any on-disk file formats; it only standardizes keys used
in PipelineResult.artifacts / PipelineResult.metadata across contests.
"""

from typing import Any, Dict, Mapping, Optional


class ArtifactKeys:
    # Config artifacts
    TRAIN_CONFIG_JSON = "train_config_json"
    TRAIN_METADATA_JSON = "train_metadata_json"
    BEST_CONFIG_JSON = "best_config_json"

    # Model artifacts
    MODELS_DIR = "models_dir"
    MODEL_DIR = "model_dir"
    MODEL_CHECKPOINT = "model_checkpoint"

    # Submission artifacts
    SUBMISSION_JSON = "submission_json"
    SUBMISSION_CSV = "submission_csv"

    # Metrics artifacts
    METRICS_JSON = "metrics_json"
    METRICS_CSV = "metrics_csv"


def artifacts_merge(*parts: Optional[Mapping[str, str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for p in parts:
        if not p:
            continue
        out.update({str(k): str(v) for k, v in dict(p).items() if v is not None})
    return out


def metadata_merge(*parts: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for p in parts:
        if not p:
            continue
        out.update(dict(p))
    return out


def capture_config_paths(
    *,
    train_config_json: str | None = None,
    train_metadata_json: str | None = None,
    best_config_json: str | None = None,
) -> Dict[str, str]:
    return {
        k: v
        for k, v in {
            ArtifactKeys.TRAIN_CONFIG_JSON: train_config_json,
            ArtifactKeys.TRAIN_METADATA_JSON: train_metadata_json,
            ArtifactKeys.BEST_CONFIG_JSON: best_config_json,
        }.items()
        if v
    }


def capture_model_paths(
    *,
    models_dir: str | None = None,
    model_dir: str | None = None,
    model_checkpoint: str | None = None,
) -> Dict[str, str]:
    return {
        k: v
        for k, v in {
            ArtifactKeys.MODELS_DIR: models_dir,
            ArtifactKeys.MODEL_DIR: model_dir,
            ArtifactKeys.MODEL_CHECKPOINT: model_checkpoint,
        }.items()
        if v
    }


def capture_submission_paths(
    *,
    submission_json: str | None = None,
    submission_csv: str | None = None,
) -> Dict[str, str]:
    return {
        k: v
        for k, v in {
            ArtifactKeys.SUBMISSION_JSON: submission_json,
            ArtifactKeys.SUBMISSION_CSV: submission_csv,
        }.items()
        if v
    }


def capture_metrics_paths(
    *,
    metrics_json: str | None = None,
    metrics_csv: str | None = None,
) -> Dict[str, str]:
    return {
        k: v
        for k, v in {
            ArtifactKeys.METRICS_JSON: metrics_json,
            ArtifactKeys.METRICS_CSV: metrics_csv,
        }.items()
        if v
    }
