"""Training loop cadence configuration (log/checkpoint frequency)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TrainingCadenceConfig:
    """When the training loop should log and checkpoint."""

    log_every_n_steps: int = 10
    log_every_n_epochs: int = 1
    checkpoint_every_n_epochs: int = 5
    checkpoint_every_n_steps: Optional[int] = None
