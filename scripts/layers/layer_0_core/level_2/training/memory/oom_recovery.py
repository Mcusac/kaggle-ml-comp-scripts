"""OOM recovery utilities."""

import gc
import time

from typing import Optional, Any

from level_0 import get_logger, get_torch
from level_1 import perform_aggressive_cleanup

logger = get_logger(__name__)
torch = get_torch()

_BYTES_PER_GB: int = 1_024 ** 3


def _log_cuda_memory(label: str) -> None:
    """Log current CUDA allocated and reserved memory."""
    try:
        allocated = torch.cuda.memory_allocated() / _BYTES_PER_GB
        reserved = torch.cuda.memory_reserved() / _BYTES_PER_GB
        logger.debug(f"Memory {label}: {allocated:.2f} GB allocated, {reserved:.2f} GB reserved")
        if label == "after" and allocated > 0.1:
            logger.warning(
                f"Memory still allocated after OOM recovery: {allocated:.2f} GB "
                f"(may indicate fragmentation)"
            )
    except RuntimeError:
        pass


def is_oom_error(exception: Exception) -> bool:
    """
    Return True if exception is an Out of Memory error.

    Args:
        exception: Exception to check.

    Returns:
        True if OOM-related, False otherwise.
    """
    if 'out of memory' in str(exception).lower():
        return True
    if torch is not None:
        try:
            return isinstance(exception, torch.OutOfMemoryError)  # type: ignore[attr-defined]
        except AttributeError:
            return False
    return False


def recover_from_oom(
    model: Optional[Any] = None,
    delay_seconds: float = 2.0,
    cleanup_passes: int = 3,
) -> None:
    """
    Recover from an OutOfMemoryError with aggressive CUDA cleanup.

    Resets CUDA memory stats, performs multiple GC+cache-flush passes with
    delays, then runs perform_aggressive_cleanup. More aggressive than routine
    cleanup — use only after an OOM.

    Args:
        model: Optional model to delete before cleanup.
        delay_seconds: Delay in seconds between cleanup passes (default: 2.0).
        cleanup_passes: Number of GC+cache-flush passes (default: 3).
    """
    if torch is None or not torch.cuda.is_available():
        return

    logger.debug("Starting OOM recovery")
    _log_cuda_memory("before")

    if model is not None:
        try:
            del model
        except Exception:
            pass
        gc.collect()

    try:
        torch.cuda.synchronize()
    except RuntimeError:
        pass

    try:
        torch.cuda.reset_peak_memory_stats()
        logger.debug("Reset CUDA memory statistics")
    except RuntimeError as e:
        raise RuntimeError("Could not reset peak memory stats") from e

    for pass_num in range(cleanup_passes):
        if pass_num > 0:
            time.sleep(delay_seconds)
            logger.debug(f"Cleanup pass {pass_num + 1}/{cleanup_passes}")
        gc.collect()
        try:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        except RuntimeError:
            pass

    perform_aggressive_cleanup()

    if delay_seconds > 0:
        time.sleep(delay_seconds)
        try:
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
        except RuntimeError:
            pass

    _log_cuda_memory("after")
    logger.debug("OOM recovery complete")