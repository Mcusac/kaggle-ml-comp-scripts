"""Generic training configuration."""

from dataclasses import dataclass
from typing import Literal, Optional

from layers.layer_0_core.level_0 import RuntimeConfig, TrainingSchema


@dataclass
class TrainingConfig(RuntimeConfig, TrainingSchema):
    """
    Full training configuration for framework-level execution.

    Inherits runtime settings (seed, device, workers) from RuntimeConfig
    and core training hyperparameters (batch_size, num_epochs, learning_rate)
    from TrainingSchema. Adds optimizer, scheduler, loss, and training mode
    configuration specific to the training loop.
    """

    # Optimizer
    optimizer: str = "AdamW"          # AdamW | Adam | SGD
    weight_decay: float = 1e-4

    # Loss function
    loss_function: str = "SmoothL1Loss"

    # Learning rate scheduler
    scheduler: Optional[str] = "ReduceLROnPlateau"   # ReduceLROnPlateau | CosineAnnealingLR | None
    scheduler_mode: str = "max"        # max for metric-based, min for loss-based
    scheduler_factor: float = 0.5
    scheduler_patience: int = 5

    # Early stopping
    early_stopping_patience: int = 10
    early_stopping_min_delta: float = 0.0

    # Mixed precision
    use_mixed_precision: bool = False
    mixed_precision_dtype: str = "float16"   # float16 | bfloat16

    # Training mode
    mode: Literal["load_or_train", "train_new", "load_only"] = "load_or_train"

    # Gradient clipping
    gradient_clip_value: Optional[float] = None