"""Training configuration builder."""

from typing import Any, Dict


def build_training_config(
    batch_size: int,
    num_epochs: int,
    learning_rate: float,
    optimizer: str,
    loss_function: str,
    scheduler: str,
    **extra: Any,
) -> Dict[str, Any]:
    """
    Build a training configuration dictionary from explicit parameters.

    No domain-specific defaults are applied. Callers provide all required
    values. Additional keyword arguments are merged in unchanged.

    Args:
        batch_size:    Number of samples per training batch.
        num_epochs:    Total number of training epochs.
        learning_rate: Initial learning rate.
        optimizer:     Optimizer identifier string (e.g. 'adam', 'sgd').
        loss_function: Loss function identifier string (e.g. 'mse', 'bce').
        scheduler:     LR scheduler identifier string (e.g. 'plateau', 'cosine').
        **extra:       Additional key-value pairs merged into the result.

    Returns:
        Training configuration dict.
    """
    config: Dict[str, Any] = {
        "batch_size":    batch_size,
        "num_epochs":    num_epochs,
        "learning_rate": learning_rate,
        "optimizer":     optimizer,
        "loss_function": loss_function,
        "scheduler":     scheduler,
    }
    config.update(extra)
    return config