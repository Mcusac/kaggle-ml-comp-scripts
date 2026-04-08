"""Runs a notebook cell safely if enabled."""

from typing import Callable, Mapping

from level_0 import get_logger, ExecutionError

logger = get_logger(__name__)


def safe_execute_cell(
    cell_id: str,
    enabled_cells: Mapping[str, bool],
    operation: Callable[[], None],
) -> None:
    """
    Safely execute a notebook cell if enabled.
    
    Wraps execution errors in ExecutionError with cell context.
    """
    if not enabled_cells.get(cell_id, False):
        logger.info(f"Cell {cell_id} skipped.")
        return

    try:
        operation()
    except Exception as exc:
        raise ExecutionError(f"Cell {cell_id} failed.") from exc
