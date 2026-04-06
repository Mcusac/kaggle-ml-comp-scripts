"""Wall-clock style deadlines for notebook-style timed runs."""

from __future__ import annotations


def train_absolute_deadline_epoch_s(total_sec: float, slack_sec: float = 0.0) -> float:
    """Return ``time.time() + total_sec - slack_sec`` (Kaggle-style session cap)."""
    import time

    return float(time.time()) + max(0.0, float(total_sec)) - max(0.0, float(slack_sec))


def train_seconds_remaining_epoch(deadline_epoch_s: float) -> float:
    """Seconds until ``deadline_epoch_s``; negative if past."""
    import time

    return float(deadline_epoch_s) - float(time.time())
