"""OOM handling utilities for CSIRO training.

CSIRO-specific wrappers around general OOM handling. Uses orchestration
core helpers (config shape) and level_2 for detection/recovery.
"""

from typing import Dict, Any, Optional, Callable, Tuple

from layers.layer_0_core.level_0 import get_logger, get_config_value
from layers.layer_0_core.level_2 import is_oom_error as _is_oom_error, recover_from_oom

_logger = get_logger(__name__)

# Defaults aligned with level_1.runtime.config.grid_search.GridSearchConfig
_DEFAULT_MIN_BATCH_SIZE = 4
_DEFAULT_BATCH_SIZE_REDUCTION_FACTOR = 2
_DEFAULT_MAX_OOM_RETRIES = 2


def _get_oom_config(config: Any) -> Tuple[int, int, int]:
    """Extract OOM config: (min_batch_size, batch_size_reduction_factor, max_oom_retries)."""
    min_bs = get_config_value(config, "grid_search.min_batch_size", default=None)
    if min_bs is None:
        min_bs = get_config_value(config, "min_batch_size", default=_DEFAULT_MIN_BATCH_SIZE)
    factor = get_config_value(config, "grid_search.batch_size_reduction_factor", default=None)
    if factor is None:
        factor = get_config_value(
            config, "batch_size_reduction_factor", default=_DEFAULT_BATCH_SIZE_REDUCTION_FACTOR
        )
    max_retries = get_config_value(config, "grid_search.max_oom_retries", default=None)
    if max_retries is None:
        max_retries = get_config_value(config, "max_oom_retries", default=_DEFAULT_MAX_OOM_RETRIES)
    return int(min_bs), int(factor), int(max_retries)


def _should_skip_retry(
    oom_retry_count: int,
    current_batch_size: int,
    min_batch_size: int,
    max_oom_retries: int,
    variant_id: str,
) -> bool:
    """Return True if we should skip retry (exhausted retries or at min batch size)."""
    if oom_retry_count >= max_oom_retries:
        _logger.warning(
            "Skipping OOM retry for %s: max retries (%d) reached",
            variant_id, max_oom_retries,
        )
        return True
    if current_batch_size <= min_batch_size:
        _logger.warning(
            "Skipping OOM retry for %s: batch_size %d <= min_batch_size %d",
            variant_id, current_batch_size, min_batch_size,
        )
        return True
    return False


def _create_skip_result(current_batch_size: int, oom_retry_count: int) -> Dict[str, Any]:
    """Create result dict for skipped OOM retry."""
    return {
        "success": False,
        "batch_size": current_batch_size,
        "oom_retry_count": oom_retry_count,
        "error": "OOM retry skipped (max retries or min batch size reached)",
    }


def _perform_oom_recovery_and_retry(
    new_batch_size: int,
    new_oom_retry_count: int,
    max_oom_retries: int,
    config: Any,
    train_func: Callable,
) -> Optional[Dict[str, Any]]:
    """Recover from OOM and retry training with reduced batch size."""
    config = _inject_batch_size(config, new_batch_size)
    recover_from_oom(model=None, delay_seconds=2.0, cleanup_passes=3)
    try:
        result = train_func(config)
        if result is None:
            return {"success": False, "error": "train_func returned None"}
        if not isinstance(result, dict):
            return {"success": False, "error": f"train_func returned {type(result).__name__}"}
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def _inject_batch_size(config: Any, batch_size: int) -> Any:
    """Inject batch_size into config for train_func. Works with dict or object config."""
    if isinstance(config, dict):
        config = dict(config)
        config.setdefault("training", {})
        if isinstance(config["training"], dict):
            config["training"] = dict(config["training"])
            config["training"]["batch_size"] = batch_size
        return config
    try:
        if not hasattr(config, "training"):
            config.training = type("Training", (), {"batch_size": batch_size})()
        else:
            config.training.batch_size = batch_size
    except Exception:
        pass
    return config


def handle_oom_error_with_retry(
    error: Exception,
    config,
    current_batch_size: int,
    oom_retry_count: int,
    variant_id: str,
    train_func: Callable
) -> Optional[Dict[str, Any]]:
    """Handle OOM error with automatic batch size reduction and retry.

    CSIRO-specific wrapper: adapts general OOM handling to CSIRO config and train_func signature.
    """
    if not _is_oom_error(error):
        return None

    min_batch_size, batch_size_reduction_factor, max_oom_retries = _get_oom_config(config)
    if _should_skip_retry(oom_retry_count, current_batch_size, min_batch_size, max_oom_retries, variant_id):
        return _create_skip_result(current_batch_size, oom_retry_count)

    new_batch_size = max(min_batch_size, current_batch_size // batch_size_reduction_factor)
    new_oom_retry_count = oom_retry_count + 1
    result = _perform_oom_recovery_and_retry(
        new_batch_size, new_oom_retry_count, max_oom_retries, config, train_func
    )
    if result is None:
        return None

    if not result.get('success') and new_oom_retry_count < max_oom_retries:
        retry_error_str = result.get('error', '')
        if 'OOM' in retry_error_str or 'out of memory' in retry_error_str.lower():
            class OOMException(Exception):
                pass
            return handle_oom_error_with_retry(
                OOMException(retry_error_str),
                config,
                new_batch_size,
                new_oom_retry_count,
                variant_id,
                train_func
            )
    return result
