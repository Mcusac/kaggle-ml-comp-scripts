"""Learning rate scheduler utilities."""

from typing import Any, Optional


def get_scheduler_mode(config: Any) -> str:
    """
    Read the scheduler mode from a config object or dict.

    Returns 'max' if the config does not specify a mode, since maximising
    a validation metric (e.g. R², accuracy) is the common case.

    Args:
        config: Config object with a .training.scheduler_mode attribute,
                a dict with a "scheduler_mode" key, or any other value.

    Returns:
        'max' or 'min'.
    """
    if hasattr(config, "training"):
        return getattr(config.training, "scheduler_mode", "max")

    if isinstance(config, dict):
        return config.get("scheduler_mode", "max")

    return "max"


def step_scheduler(
    scheduler: Optional[Any],
    config: Any,
    primary_metric_value: float,
    val_loss: float,
) -> None:
    """
    Advance a learning rate scheduler by one step.

    Chooses the metric passed to scheduler.step() based on the configured
    scheduler mode:
      - 'max' mode: uses primary_metric_value (e.g. weighted R², accuracy, F1)
      - 'min' mode: uses val_loss

    The caller is responsible for computing and naming the primary metric.
    This function does not care what the metric is, only its value.

    Args:
        scheduler:             Scheduler instance, or None (no-op if None).
        config:                Config used to determine scheduler mode.
        primary_metric_value:  Current value of the primary tracking metric.
        val_loss:              Current validation loss.
    """
    if scheduler is None:
        return

    if get_scheduler_mode(config) == "max":
        scheduler.step(primary_metric_value)
    else:
        scheduler.step(val_loss)