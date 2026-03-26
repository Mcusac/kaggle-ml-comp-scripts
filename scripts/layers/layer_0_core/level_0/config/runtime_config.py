"""Runtime configuration (seed, device, paths)."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RuntimeConfig:
    """
    Runtime configuration base with common settings (seed, device, paths).

    All runtime-specific configs (TrainingConfig, EvaluationConfig, GridSearchConfig)
    should extend this class.
    """
    # Reproducibility
    seed: int = 42

    # Device configuration
    device: str = 'auto'  # 'auto', 'cuda', 'cpu', 'cuda:0', etc.
    num_workers: int = 4

    # Output configuration
    output_dir: str = 'output'
    log_dir: Optional[str] = None  # If None, uses output_dir/logs

    # Misc
    verbose: bool = True
    debug: bool = False

    def __post_init__(self):
        """Post-initialization validation and setup."""
        if self.log_dir is None:
            self.log_dir = str(Path(self.output_dir) / 'logs')
