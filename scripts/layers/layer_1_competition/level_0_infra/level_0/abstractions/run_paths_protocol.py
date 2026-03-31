"""Protocol for contest output layout (runs, artifacts under output dir)."""

from pathlib import Path
from typing import Protocol


class ContestRunPathsProtocol(Protocol):
    """Minimal surface for resolving contest output / working directories."""

    def get_output_dir(self) -> Path:
        """Base output directory (e.g. Kaggle working or local output)."""
        ...
