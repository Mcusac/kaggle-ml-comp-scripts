"""Regression ensemble result handler."""

from typing import Dict, Any, List

from layers.layer_0_core.level_2 import log_pipeline_completion


def handle_regression_ensemble_result(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    ensemble_config: Dict[str, Any]
) -> None:
    """
    Handle regression ensemble pipeline result.

    Args:
        returncode: Process return code
        stdout_lines: Standard output lines
        log_file: Log file path
        ensemble_config: Ensemble configuration used
    """
    log_items = [
        ("Model types", ensemble_config.get("model_types", [])),
        ("Method", ensemble_config.get("method", "weighted_average")),
    ]
    log_pipeline_completion(
        returncode, stdout_lines, log_file,
        "Regression Ensemble Pipeline",
        log_items,
    )
