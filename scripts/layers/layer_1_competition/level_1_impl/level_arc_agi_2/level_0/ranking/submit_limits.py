"""ARC submission limit: optional environment-variable cap on evaluation tasks."""

import os

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def read_submit_max_tasks_env() -> int | None:
    """Optional tune-only cap on max evaluation tasks (ARC26_SUBMIT_MAX_TASKS env var).

    Returns the positive integer value, or None if unset / invalid.
    """
    raw = os.environ.get("ARC26_SUBMIT_MAX_TASKS", "").strip()
    if not raw:
        return None
    try:
        n = int(raw)
        return n if n > 0 else None
    except ValueError:
        _logger.warning("Invalid ARC26_SUBMIT_MAX_TASKS=%r; ignoring", raw)
        return None