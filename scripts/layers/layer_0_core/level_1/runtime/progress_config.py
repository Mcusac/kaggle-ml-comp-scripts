"""
Progress display configuration.

Provides:
- ProgressVerbosity: verbosity level enum
- ProgressConfig: dataclass for display settings
  Construct directly for explicit values.
  Use ProgressConfig.from_env() to apply environment variable overrides.
"""

import os

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

from level_0 import ConfigValidationError, get_logger

logger = get_logger(__name__)


class ProgressVerbosity(IntEnum):
    SILENT = 0
    MINIMAL = 1
    MODERATE = 2
    DETAILED = 3
    DEBUG = 4


_VERBOSITY_MAP = {
    "silent": ProgressVerbosity.SILENT,
    "minimal": ProgressVerbosity.MINIMAL,
    "moderate": ProgressVerbosity.MODERATE,
    "detailed": ProgressVerbosity.DETAILED,
    "debug": ProgressVerbosity.DEBUG,
}


def _parse_env_verbosity() -> Optional[ProgressVerbosity]:
    """
    Read PROGRESS_VERBOSITY from the environment.

    Returns the parsed ProgressVerbosity, or None if unset or unrecognised.
    Logs a warning on unrecognised values — the caller applies its own default.
    """
    val = os.environ.get("PROGRESS_VERBOSITY")
    if val is None:
        return None

    try:
        return ProgressVerbosity(int(val))
    except ValueError:
        pass

    result = _VERBOSITY_MAP.get(val.strip().lower())
    if result is None:
        logger.warning(
            "Invalid PROGRESS_VERBOSITY=%r; use 0-4 or "
            "silent|minimal|moderate|detailed|debug. Ignoring.",
            val,
        )
    return result


def _is_progress_disabled() -> bool:
    return os.environ.get("PROGRESS_DISABLE", "").strip().lower() in {"1", "true", "yes"}


@dataclass
class ProgressConfig:
    """
    Display-related progress configuration.

    Construct directly to set all values explicitly.
    Use ProgressConfig.from_env() to apply PROGRESS_VERBOSITY and
    PROGRESS_DISABLE environment variable overrides on top of defaults.

    Note: cadence (log/checkpoint frequency) lives in TrainingCadenceConfig.
    """
    verbosity: ProgressVerbosity = ProgressVerbosity.MODERATE
    show_progress_bar: bool = True
    progress_bar_ncols: int = 100
    progress_bar_leave: bool = True
    show_eta: bool = True
    eta_smoothing: float = 0.3
    show_epoch_progress: bool = True
    show_batch_progress: bool = True
    show_metrics_in_progress: bool = True
    show_data_loading: bool = True
    show_memory_stats: bool = True
    refresh_rate: float = 0.5

    def __post_init__(self) -> None:
        if self.refresh_rate <= 0:
            raise ConfigValidationError(
                f"refresh_rate must be positive, got {self.refresh_rate}"
            )

    @classmethod
    def from_env(cls, **overrides) -> "ProgressConfig":
        """
        Construct a ProgressConfig with environment variable overrides applied.

        PROGRESS_DISABLE=1|true|yes forces verbosity to SILENT.
        PROGRESS_VERBOSITY=<0-4 or name> sets verbosity if valid.

        Keyword arguments are applied after env resolution, allowing
        callers to combine env-driven defaults with explicit overrides.
        """
        if _is_progress_disabled():
            verbosity = ProgressVerbosity.SILENT
        else:
            verbosity = _parse_env_verbosity() or ProgressVerbosity.MODERATE

        return cls(verbosity=verbosity, **overrides)