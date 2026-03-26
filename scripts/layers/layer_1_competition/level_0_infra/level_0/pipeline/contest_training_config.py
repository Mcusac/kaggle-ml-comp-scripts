"""Contest-specific training configuration utilities."""

from typing import Dict, Any

from layers.layer_0_core.level_0 import build_training_config


DEFAULT_TRAINING_SETTINGS = {
    "scheduler_mode": "max",
    "scheduler_factor": 0.5,
    "scheduler_patience": 5,
    "early_stopping_patience": 10,
    "weight_decay": 1e-4,
    "use_mixed_precision": False,
    "num_workers": 4,
    "pin_memory": True,
    "use_multi_gpu": False,
}


def create_training_config(
    batch_size: int,
    num_epochs: int,
    learning_rate: float,
    optimizer: str,
    loss_function: str,
    scheduler: str,
    config,
) -> Dict[str, Any]:
    """
    Create training configuration with contest defaults.
    """

    training_config = build_training_config(
        batch_size=batch_size,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        optimizer=optimizer,
        loss_function=loss_function,
        scheduler=scheduler,
        **DEFAULT_TRAINING_SETTINGS,
    )

    # Merge defaults into config.training if present
    if hasattr(config, "training"):
        for key, value in training_config.items():
            if not hasattr(config.training, key):
                setattr(config.training, key, value)

    return training_config
