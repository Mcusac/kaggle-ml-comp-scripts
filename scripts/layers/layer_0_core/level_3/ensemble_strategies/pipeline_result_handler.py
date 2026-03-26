"""Ensemble pipeline result handler."""

from typing import List

from layers.layer_0_core.level_0 import is_kaggle
from layers.layer_0_core.level_1 import resolve_environment_path

from level_2 import _log_pipeline_completion


def handle_ensemble_result(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    model_paths: List[str],
    method: str,
    score_type: str,
    model: str,
) -> None:
    """
    Handle result from ensemble pipeline.

    Args:
        returncode: Process return code.
        stdout_lines: Last N lines of stdout output.
        log_file: Path to log file (for error messages).
        model_paths: List of model paths used in ensemble.
        method: Ensembling method used.
        score_type: Score type used for weighting.
        model: Model architecture name.
    """
    log_items = [
        ("Models used", len(model_paths)),
        ("Method", method),
        ("Score type", score_type),
        ("Model architecture", model),
    ]
    submission_path = "/kaggle/working/submission.csv" if is_kaggle() else resolve_environment_path("submission.csv", purpose="output")
    success_footer = [
        "\nSubmission saved to:",
        f"   {submission_path}",
        "\nNext steps:",
        "   1. Review submission.csv",
        "   2. Submit to Kaggle competition",
    ]
    _log_pipeline_completion(
        returncode, stdout_lines, log_file,
        "Ensemble pipeline",
        log_items,
        success_header="Ensemble submission generated successfully!",
        success_footer=success_footer,
    )