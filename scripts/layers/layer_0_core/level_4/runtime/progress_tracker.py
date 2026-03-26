"""
Main unified progress tracking system.

Coordinates progress bars, metrics calculation, and formatting.
Injects runtime dependencies for clean separation of concerns.
"""

from typing import Optional, Any, Dict

from level_0 import get_logger
from level_1 import ProgressConfig, get_device_info
from level_2 import ProgressMetrics, ProgressBarManager
from level_3 import ProgressFormatter

logger = get_logger(__name__)


class ProgressTracker:
    """
    Main progress tracking interface.
    
    Manages progress bars with unified configuration, metrics, and formatting.
    """
    
    def __init__(self, config: ProgressConfig):
        self.config = config
        self.bar_manager = ProgressBarManager(config.verbosity)
        
        # Inject memory info provider into metrics
        self.metrics = ProgressMetrics(
            config,
            memory_info_provider=self._get_device_memory_info,
        )
        self.formatter = ProgressFormatter(config)

    @staticmethod
    def _get_device_memory_info() -> Dict[str, str]:
        """
        Get GPU device info if runtime is available.
        
        Returns:
            Dictionary with GPU count and names, or empty dict if unavailable
        """
        info: Dict[str, str] = {}
        try:
            device_info = get_device_info()
            if device_info["cuda_available"]:
                info["GPU_count"] = str(device_info["device_count"])
                info["GPU_names"] = ", ".join(device_info["device_names"])
        except Exception:
            # Fail gracefully if device info fetch errors
            pass
        return info

    def create_bar(
        self,
        bar_id: str,
        total: int,
        desc: str,
        level: int = 1,
        unit: str = "it",
        initial: int = 0,
        **kwargs
    ) -> Optional[str]:
        """
        Create a new progress bar.
        
        Args:
            bar_id: Unique identifier for the bar
            total: Total number of iterations
            desc: Description displayed in bar
            level: Hierarchy level (1=top, 2+=nested)
            unit: Unit of iteration (default: "it")
            initial: Starting count (default: 0)
            **kwargs: Additional arguments for tqdm
            
        Returns:
            bar_id if created, None if hidden due to verbosity
        """
        bar_id_created = self.bar_manager.create_bar(
            bar_id, total, desc, level, unit, initial, **kwargs
        )
        if bar_id_created:
            self.metrics.register_bar(bar_id)
        return bar_id_created

    def update(self, bar_id: str, n: int = 1, **metrics_kwargs: Any) -> None:
        """
        Update a progress bar.
        
        Args:
            bar_id: ID of the bar to update
            n: Number of items to advance (default: 1)
            **metrics_kwargs: Additional metrics to display in postfix
        """
        bar = self.bar_manager.get_bar(bar_id)
        if not bar:
            return
        postfix = self.formatter.format_postfix(
            bar_id, self.metrics, self.bar_manager, **metrics_kwargs
        )
        if postfix:
            bar.set_postfix(postfix)
        bar.update(n)
        self.metrics.record_update(bar_id, n)

    def set_postfix(self, bar_id: str, **metrics_kwargs: Any) -> None:
        """
        Update postfix without advancing the bar.
        
        Args:
            bar_id: ID of the bar to update
            **metrics_kwargs: Metrics to display in postfix
        """
        bar = self.bar_manager.get_bar(bar_id)
        if not bar:
            return
        postfix = self.formatter.format_postfix(
            bar_id, self.metrics, self.bar_manager, **metrics_kwargs
        )
        if postfix:
            bar.set_postfix(postfix)

    def close(self, bar_id: str) -> None:
        """Close a single progress bar."""
        self.bar_manager.close(bar_id)
        self.metrics.cleanup(bar_id)

    def close_all(self) -> None:
        """Close all active progress bars."""
        self.bar_manager.close_all()
        for bar_id in list(self.metrics.start_times.keys()):
            self.metrics.cleanup(bar_id)

    def get_elapsed_time(self, bar_id: str) -> Optional[float]:
        """Get elapsed time for a bar in seconds."""
        return self.metrics.get_elapsed_time(bar_id)