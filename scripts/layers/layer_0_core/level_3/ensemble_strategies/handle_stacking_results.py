"""Handles results from stacking pipeline execution."""

from typing import Any, Dict, List

from level_2 import log_pipeline_completion


def handle_stacking_result(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    stacking_config: Dict[str, Any],
    operation_name: str = "Stacking pipeline",
) -> None:
    """
    Handle stacking or stacking ensemble pipeline result.

    Args:
        returncode: Process return code.
        stdout_lines: Captured stdout lines.
        log_file: Path to the pipeline log file.
        stacking_config: Config dict with keys model_types, meta_model_alpha, n_folds.
        operation_name: Human-readable label for log output.
    """
    log_items = [
        ("Model types", stacking_config.get("model_types", [])),
        ("Meta-model alpha", stacking_config.get("meta_model_alpha", 10.0)),
        ("Number of folds", stacking_config.get("n_folds", 5)),
    ]
    log_pipeline_completion(
        returncode, stdout_lines, log_file, operation_name, log_items
    )


def handle_hybrid_stacking_result(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    hybrid_stacking_config: Dict[str, Any],
) -> None:
    """
    Handle hybrid stacking pipeline result.

    Args:
        returncode: Process return code.
        stdout_lines: Captured stdout lines.
        log_file: Path to the pipeline log file.
        hybrid_stacking_config: Config dict with keys regression_ensembles,
            end_to_end_ensembles, meta_model_alpha, n_folds.
    """
    regression_ensembles = hybrid_stacking_config.get("regression_ensembles", {})
    end_to_end_ensembles = hybrid_stacking_config.get("end_to_end_ensembles", {})
    log_items = [
        ("Regression ensembles", regression_ensembles.get("model_types", [])),
        ("End-to-end ensembles", end_to_end_ensembles.get("model_name", "N/A")),
        ("Meta-model alpha", hybrid_stacking_config.get("meta_model_alpha", 10.0)),
        ("Number of folds", hybrid_stacking_config.get("n_folds", 5)),
    ]
    log_pipeline_completion(
        returncode, stdout_lines, log_file, "Hybrid stacking pipeline", log_items
    )