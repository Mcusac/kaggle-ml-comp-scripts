"""
Manages tqdm progress bars, their positions, and metadata.

Responsibilities:
- Create and track active progress bars
- Handle bar positioning for nested/hierarchical progress
- Manage bar lifecycle (creation, update, closure)
- Store and retrieve bar metadata for formatting
"""

from tqdm import tqdm
from typing import Dict, Optional, Any, Union

from level_1 import ProgressVerbosity


class ProgressBarManager:
    BAR_FORMAT = "{desc}: {percentage:3.0f}%|{bar}| {n}/{total} [{rate_fmt}{postfix}]"

    def __init__(self, verbosity: Union[int, ProgressVerbosity] = ProgressVerbosity.MODERATE):
        self.verbosity: int = int(verbosity) if isinstance(verbosity, ProgressVerbosity) else verbosity
        self.active_bars: Dict[str, tqdm] = {}
        self.bar_metadata: Dict[str, Dict[str, Any]] = {}

    def should_show(self, level: int = 1) -> bool:
        """Determine if a bar at given level should be displayed."""
        if self.verbosity <= 0:
            return False
        if self.verbosity == 1:
            return level == 1
        return True

    def get_position(self, level: int) -> int:
        """Get the tqdm position for a bar at given hierarchy level."""
        return level - 1

    def create_bar(
        self,
        bar_id: str,
        total: int,
        desc: str,
        level: int = 1,
        unit: str = "it",
        initial: int = 0,
        leave: Optional[bool] = None,
        disable: Optional[bool] = None,
        **kwargs: Any
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
            leave: Whether to leave bar after completion
            disable: Whether to disable the bar
            **kwargs: Additional tqdm arguments

        Returns:
            bar_id if created, None if hidden due to verbosity
        """
        visible = self.should_show(level)
        if not visible:
            return None
        if bar_id in self.active_bars:
            self.close(bar_id)

        position = self.get_position(level)
        leave = leave if leave is not None else (level == 1)
        disable = disable if disable is not None else False

        bar = tqdm(
            total=total,
            desc=desc,
            unit=unit,
            initial=initial,
            position=position,
            leave=leave,
            disable=disable,
            bar_format=self.BAR_FORMAT,
            **kwargs,
        )

        self.active_bars[bar_id] = bar
        self.bar_metadata[bar_id] = {
            "level": level,
            "total": total,
            "unit": unit,
            "desc": desc,
        }

        return bar_id

    def get_bar(self, bar_id: str) -> Optional[tqdm]:
        """Get a progress bar by ID."""
        return self.active_bars.get(bar_id)

    def get_metadata(self, bar_id: str) -> Dict[str, Any]:
        """Get metadata for a progress bar by ID."""
        return self.bar_metadata.get(bar_id, {})

    def close(self, bar_id: str) -> None:
        """Close and remove a progress bar."""
        bar = self.active_bars.pop(bar_id, None)
        if bar:
            bar.close()
        self.bar_metadata.pop(bar_id, None)

    def close_all(self) -> None:
        """Close all active progress bars."""
        for bar_id in list(self.active_bars.keys()):
            self.close(bar_id)
