"""Validate execution result and raise ExecutionError if failed."""

from level_0 import ExecutionError, ExecutionResult


def validate_execution_result(
    result: ExecutionResult,
    operation_name: str,
) -> None:
    """
    Validate execution result and raise ExecutionError if failed.
    """
    if result.succeeded:
        return

    error_msg = f"{operation_name} failed with return code {result.returncode}"

    if result.output:
        error_msg += "\n\nOutput:\n" + "\n".join(result.output)

    if result.log_file:
        error_msg += f"\n\nFull output available in: {result.log_file}"

    raise ExecutionError(error_msg)
