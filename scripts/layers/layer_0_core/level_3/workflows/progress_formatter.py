"""
Formats progress bar output and metrics display.

Responsibilities:
- Format ETA and elapsed time
- Format throughput and performance metrics
- Build postfix strings for tqdm
- Respect verbosity settings for output detail
"""

from typing import Dict, Any, Optional

from layers.layer_0_core.level_1 import ProgressConfig, ProgressVerbosity
from layers.layer_0_core.level_2 import ProgressMetrics


class ProgressFormatter:
    """Formats metrics and postfix for tqdm progress bars."""

    def __init__(self, config: ProgressConfig):
        self.config = config

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format seconds into human-readable time string."""
        if seconds < 60:
            return f"{int(seconds)}s"

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"

        return f"{minutes}m {secs}s"

    def format_postfix(
        self,
        bar_id: str,
        metrics: "ProgressMetrics",
        current: int,
        total: Optional[int] = None,
        unit: str = "it",
        **metrics_kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build postfix dictionary for tqdm bar.

        Includes ETA, memory stats, and throughput based on verbosity.

        Args:
            bar_id: ID of the progress bar
            metrics: ProgressMetrics instance
            current: Current progress value (bar.n)
            total: Total iterations for the bar
            unit: tqdm unit label
            **metrics_kwargs: Additional metrics to include in postfix

        Returns:
            Dictionary of postfix values for tqdm
        """
        postfix: Dict[str, Any] = dict(metrics_kwargs)

        # ETA (MODERATE verbosity)
        if (
            self.config.verbosity >= ProgressVerbosity.MODERATE
            and total is not None
            and self.config.show_eta
        ):
            eta_sec = metrics.estimate_eta(bar_id, current, total)
            if eta_sec:
                postfix["eta"] = self.format_time(eta_sec)

        # Memory stats (DETAILED verbosity)
        if (
            self.config.verbosity >= ProgressVerbosity.DETAILED
            and self.config.show_memory_stats
        ):
            mem_info = metrics.get_memory_info()
            postfix.update(mem_info)

        # Throughput (DETAILED verbosity)
        if self.config.verbosity >= ProgressVerbosity.DETAILED:
            throughput = metrics.calculate_throughput(bar_id, current)
            if throughput is not None:
                postfix[f"{unit}/s"] = f"{throughput:.1f}"

        return postfix