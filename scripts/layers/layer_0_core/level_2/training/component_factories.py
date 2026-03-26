"""Training component factories: optimizer, scheduler, loss function."""

from typing import Any, Dict, Optional, Type, Union

from layers.layer_0_core.level_0 import get_logger, get_torch, get_config_value
from layers.layer_0_core.level_1 import (
    FocalLoss,
    WeightedBCELoss,
    SparseBCEWithLogitsLoss,
    LabelSmoothingBCEWithLogitsLoss,
)

torch = get_torch()
nn = torch.nn
optim = torch.optim
logger = get_logger(__name__)

# Registry of all available loss functions.
# Keyed by normalised lowercase name (underscores and spaces stripped).
# Accepts both class-name keys ("mseloss") and short keys ("mse").
# To add a loss without modifying this file, pass a custom registry
# to create_loss_function().
_DEFAULT_LOSS_REGISTRY: Dict[str, Type[nn.Module]] = {
    # PyTorch built-ins — class-name keys
    "smoothl1loss":         nn.SmoothL1Loss,
    "mseloss":              nn.MSELoss,
    "l1loss":               nn.L1Loss,
    "crossentropyloss":     nn.CrossEntropyLoss,
    "bcewithlogitsloss":    nn.BCEWithLogitsLoss,
    # PyTorch built-ins — short keys
    "mse":                  nn.MSELoss,
    "mae":                  nn.L1Loss,
    "l1":                   nn.L1Loss,
    "huber":                nn.SmoothL1Loss,
    "smoothl1":             nn.SmoothL1Loss,
    "bce":                  nn.BCEWithLogitsLoss,
    # Custom losses — class-name keys
    "focalloss":                        FocalLoss,
    "weightedbceloss":                  WeightedBCELoss,
    "sparsebcewithlogitsloss":          SparseBCEWithLogitsLoss,
    "labelsmoothingbcewithlogitsloss":  LabelSmoothingBCEWithLogitsLoss,
    # Custom losses — short keys
    "focal":            FocalLoss,
    "weightedbce":      WeightedBCELoss,
    "sparsebce":        SparseBCEWithLogitsLoss,
    "labelsmoothing":   LabelSmoothingBCEWithLogitsLoss,
}


def _get_param_or_config(
    param: Optional[Any],
    config: Union[Any, Dict[str, Any]],
    config_path: str,
    default: Any,
) -> Any:
    """Return param if not None, else extract from config via dot-notation path."""
    if param is not None:
        return param
    return get_config_value(config, config_path, default=default)


def create_optimizer(
    model: nn.Module,
    config: Union[Any, Dict[str, Any]],
    learning_rate: Optional[float] = None,
    weight_decay: Optional[float] = None,
    optimizer: Optional[str] = None,
    **kwargs,
) -> optim.Optimizer:
    """
    Create an optimizer from config or explicit parameters.

    Args:
        model: Model whose parameters will be optimized.
        config: Config object or dict.
        learning_rate: Override config learning rate.
        weight_decay: Override config weight decay.
        optimizer: Override config optimizer type ('AdamW', 'Adam', 'SGD').
        **kwargs: Additional arguments forwarded to the optimizer constructor.

    Returns:
        Configured optimizer instance.
    """
    opt_type = _get_param_or_config(optimizer, config, "training.optimizer", "AdamW")
    lr = _get_param_or_config(learning_rate, config, "training.learning_rate", 1e-3)
    wd = _get_param_or_config(weight_decay, config, "training.weight_decay", 1e-4)

    if opt_type == "AdamW":
        result = optim.AdamW(model.parameters(), lr=lr, weight_decay=wd, **kwargs)
    elif opt_type == "Adam":
        result = optim.Adam(model.parameters(), lr=lr, weight_decay=wd, **kwargs)
    elif opt_type == "SGD":
        momentum = kwargs.pop("momentum", 0.9)
        result = optim.SGD(model.parameters(), lr=lr, weight_decay=wd, momentum=momentum, **kwargs)
    else:
        raise ValueError(f"Unknown optimizer: {opt_type!r}. Valid: AdamW, Adam, SGD")

    logger.info("Created optimizer: %s (lr=%s, wd=%s)", opt_type, lr, wd)
    return result


def create_scheduler(
    optimizer: optim.Optimizer,
    config: Union[Any, Dict[str, Any]],
    scheduler: Optional[str] = None,
    num_epochs: Optional[int] = None,
    scheduler_mode: Optional[str] = None,
    scheduler_factor: Optional[float] = None,
    scheduler_patience: Optional[int] = None,
    **kwargs,
) -> Optional[optim.lr_scheduler._LRScheduler]:
    """
    Create a learning rate scheduler from config or explicit parameters.

    Args:
        optimizer: Optimizer to schedule.
        config: Config object or dict.
        scheduler: Override config scheduler type.
        num_epochs: Override config epoch count (used by CosineAnnealingLR).
        scheduler_mode: Override config mode ('min' or 'max').
        scheduler_factor: Override config reduction factor.
        scheduler_patience: Override config patience.
        **kwargs: Additional arguments forwarded to the scheduler constructor.

    Returns:
        Configured scheduler instance, or None if type is unrecognised.
    """
    sched_type = _get_param_or_config(scheduler, config, "training.scheduler", "ReduceLROnPlateau")
    epochs   = _get_param_or_config(num_epochs, config, "training.num_epochs", 100)
    mode     = _get_param_or_config(scheduler_mode, config, "training.scheduler_mode", "max")
    factor   = _get_param_or_config(scheduler_factor, config, "training.scheduler_factor", 0.5)
    patience = _get_param_or_config(scheduler_patience, config, "training.scheduler_patience", 5)

    if sched_type == "ReduceLROnPlateau":
        result = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode=mode, factor=factor, patience=patience, verbose=False, **kwargs
        )
    elif sched_type == "CosineAnnealingLR":
        result = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, **kwargs)
    else:
        logger.info("No scheduler configured (type: %s)", sched_type)
        return None

    logger.info("Created scheduler: %s", sched_type)
    return result


def create_loss_function(
    config: Union[Any, Dict[str, Any]],
    loss_function: Optional[str] = None,
    registry: Optional[Dict[str, Type[nn.Module]]] = None,
    **kwargs,
) -> nn.Module:
    """
    Create a loss function from config or an explicit name.

    Accepts both class-name keys (e.g. 'MSELoss', 'BCEWithLogitsLoss') and
    short keys (e.g. 'mse', 'bce', 'focal'). Keys are normalised to lowercase
    with underscores and spaces stripped before lookup.

    Args:
        config: Config object or dict (dot-notation path: training.loss_function).
        loss_function: Override the config value.
        registry: Optional {normalised_name: class} dict to inject additional
                  or replacement loss types without modifying this file.
        **kwargs: Passed to the loss class constructor.

    Returns:
        Instantiated loss module.

    Raises:
        TypeError: If loss_function resolves to a non-string.
        ValueError: If the name is not in the registry, or kwargs are invalid.
    """
    effective_registry = {**_DEFAULT_LOSS_REGISTRY, **(registry or {})}

    loss_name = _get_param_or_config(loss_function, config, "training.loss_function", "SmoothL1Loss")
    if not isinstance(loss_name, str) or not loss_name:
        raise TypeError(f"loss_function must be a non-empty str, got {loss_name!r}")

    loss_key = loss_name.lower().replace("_", "").replace(" ", "")
    if loss_key not in effective_registry:
        valid = ", ".join(sorted(effective_registry))
        raise ValueError(f"Unknown loss function: {loss_name!r}. Valid: {valid}")

    loss_class = effective_registry[loss_key]
    try:
        return loss_class(**kwargs)
    except TypeError as e:
        raise ValueError(f"Invalid arguments for {loss_name}: {e}") from e