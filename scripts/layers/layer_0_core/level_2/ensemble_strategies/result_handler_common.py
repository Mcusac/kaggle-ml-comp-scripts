"""Shared logic for pipeline result handlers."""

from typing import Any, List, Optional, Tuple

from layers.layer_0_core.level_0 import ExecutionResult, get_logger
from layers.layer_0_core.level_1 import validate_execution_result

_logger = get_logger(__name__)


def log_pipeline_completion(
    returncode: int,
    stdout_lines: List[str],
    log_file: str,
    operation_name: str,
    log_items: List[Tuple[str, Any]],
    success_header: Optional[str] = None,
    success_footer: Optional[List[str]] = None,
) -> None:
    if returncode != 0:
        _logger.error(f"{operation_name} failed with return code {returncode}")
        result = ExecutionResult(returncode=returncode, output=stdout_lines, log_file=log_file or None)
        validate_execution_result(result, operation_name)

    _logger.info("=" * 60)
    _logger.info(success_header or f"{operation_name} Completed Successfully")
    _logger.info("=" * 60)
    for label, value in log_items:
        _logger.info(f"  {label}: {value}")
    _logger.info(f"  Log file: {log_file}")
    if success_footer:
        for line in success_footer:
            _logger.info(line)
    else:
        _logger.info("\n✅ Submission file generated successfully!")
        _logger.info("   Check output directory for submission.csv")
