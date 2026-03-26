"""
Calculates ETA, throughput, and elapsed time for progress bars.

Uses dependency injection for optional memory/GPU info to maintain
clean separation from runtime dependencies.
"""

import time

from typing import Dict, Optional, Callable
from collections import deque

from layers.layer_0_core.level_1 import ProgressConfig


class ProgressMetrics:
    """
    Tracks timing and performance metrics for progress bars.

    Attributes:
        config: ProgressConfig instance
        memory_info_provider: Optional callback for memory/device info
    """

    def __init__(
        self,
        config: ProgressConfig,
        memory_info_provider: Optional[Callable[[], Dict[str, str]]] = None,
    ):
        self.config = config
        self.memory_info_provider = memory_info_provider
        self.start_times: Dict[str, float] = {}
        self.last_update_times: Dict[str, float] = {}
        self.update_counts: Dict[str, deque] = {}

    def register_bar(self, bar_id: str) -> None:
        """Register a bar and start timing."""
        now = time.time()
        self.start_times[bar_id] = now
        self.last_update_times[bar_id] = now
        self.update_counts[bar_id] = deque(maxlen=10)

    def cleanup(self, bar_id: str) -> None:
        """Clean up tracking data for a bar."""
        self.start_times.pop(bar_id, None)
        self.last_update_times.pop(bar_id, None)
        self.update_counts.pop(bar_id, None)

    def record_update(self, bar_id: str, n: int) -> None:
        """Record an update and calculate rate."""
        if bar_id not in self.last_update_times:
            return
        now = time.time()
        elapsed = now - self.last_update_times[bar_id]
        if elapsed > 0:
            rate = n / elapsed
            self.update_counts[bar_id].append(rate)
        self.last_update_times[bar_id] = now

    def estimate_eta(self, bar_id: str, current: int, total: Optional[int]) -> Optional[float]:
        """
        Estimate time to completion based on current rate.

        Args:
            bar_id: ID of the progress bar
            current: Current count
            total: Total count

        Returns:
            Estimated seconds until completion, or None if unavailable
        """
        if bar_id not in self.start_times or total is None or current >= total:
            return None
        rates = self.update_counts.get(bar_id, deque())
        avg_rate = sum(rates) / len(rates) if rates else (current / (time.time() - self.start_times[bar_id]))
        if avg_rate <= 0:
            return None
        return (total - current) / avg_rate

    def calculate_throughput(self, bar_id: str, current: int) -> Optional[float]:
        """
        Calculate average throughput (items per second).

        Args:
            bar_id: ID of the progress bar
            current: Current count

        Returns:
            Items per second, or None if unavailable
        """
        if bar_id not in self.start_times:
            return None
        elapsed = time.time() - self.start_times[bar_id]
        if elapsed <= 0:
            return None
        return current / elapsed

    def get_memory_info(self) -> Dict[str, str]:
        """
        Get GPU/device memory info via injected provider.

        Returns:
            Dictionary of memory info, or empty dict if provider unavailable
        """
        if self.memory_info_provider is None:
            return {}
        try:
            return self.memory_info_provider()
        except Exception:
            return {}

    def get_elapsed_time(self, bar_id: str) -> Optional[float]:
        """Get total elapsed time for a bar."""
        if bar_id not in self.start_times:
            return None
        return time.time() - self.start_times[bar_id]
