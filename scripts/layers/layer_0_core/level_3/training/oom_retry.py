"""Generic OOM retry utilities."""

from typing import Any, Callable, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import is_oom_error, recover_from_oom

_logger = get_logger(__name__)


def handle_oom_error_with_retry(
    func: Callable[..., Any],
    *args: Any,
    batch_size_key: str = "batch_size",
    initial_batch_size: Optional[int] = None,
    min_batch_size: int = 1,
    reduction_factor: float = 0.5,
    max_retries: int = 3,
    on_retry: Optional[Callable[[int], None]] = None,
    raise_on_failure: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Execute a function with automatic retry on CUDA OOM errors by reducing batch size.

    This is a generic retry engine. It does not know anything about configs,
    training pipelines, or result formats.

    Args:
        func:
            Function to execute.

        *args:
            Positional arguments passed to the function.

        batch_size_key:
            Keyword argument name used for batch size.

        initial_batch_size:
            Starting batch size. If None, taken from kwargs[batch_size_key].

        min_batch_size:
            Minimum batch size allowed.

        reduction_factor:
            Factor applied to batch size when retrying (0.5 = halve).

        max_retries:
            Maximum number of retries.

        on_retry:
            Optional callback invoked after batch size reduction.
            Receives the new batch size. Useful if the caller needs to
            update config objects.

        raise_on_failure:
            If True, raises RuntimeError when retries are exhausted.
            If False, returns None instead.

        **kwargs:
            Keyword arguments passed to the function.

    Returns:
        Result of the function execution.

    Raises:
        RuntimeError if OOM persists and raise_on_failure=True.
    """

    if initial_batch_size is None:
        if batch_size_key not in kwargs:
            raise ValueError(
                f"batch_size_key '{batch_size_key}' not found in kwargs"
            )
        initial_batch_size = kwargs[batch_size_key]

    current_batch_size = initial_batch_size
    retry_count = 0

    while True:
        try:
            kwargs[batch_size_key] = current_batch_size
            return func(*args, **kwargs)

        except Exception as e:
            if not is_oom_error(e):
                raise

            if retry_count >= max_retries or current_batch_size <= min_batch_size:
                _logger.error(
                    "⚠️ Persistent CUDA OOM after %s retries with batch_size=%s",
                    retry_count,
                    current_batch_size,
                )

                if raise_on_failure:
                    raise RuntimeError(
                        f"OOM persists after {retry_count} retries "
                        f"(batch_size={current_batch_size}, min_batch_size={min_batch_size})"
                    ) from e

                return None

            retry_count += 1

            new_batch_size = max(
                min_batch_size,
                int(current_batch_size * reduction_factor),
            )

            _logger.warning(
                "⚠️ CUDA OOM detected with batch_size=%s (retry %s/%s)",
                current_batch_size,
                retry_count,
                max_retries,
            )

            _logger.info("   Retrying with reduced batch_size=%s", new_batch_size)
            _logger.info("   Performing OOM recovery...")

            recover_from_oom(
                model=None,
                delay_seconds=2.0,
                cleanup_passes=3,
            )

            if on_retry is not None:
                on_retry(new_batch_size)

            current_batch_size = new_batch_size