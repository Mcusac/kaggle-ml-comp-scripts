"""Checkpoint loading utilities for CSIRO feature extraction models."""

from pathlib import Path
from typing import Any, Dict

from layers.layer_0_core.level_0 import get_logger, get_torch

_torch = get_torch()
_logger = get_logger(__name__)


def load_model_from_checkpoint(
    model: Any,
    path: Path,
    device: Any
) -> Dict[str, Any]:
    """Load checkpoint state dict into a model.

    Handles DataParallel-wrapped models. Uses weights_only=False to support
    checkpoints with extra metadata (e.g. model_name).

    Args:
        model: PyTorch model to load weights into.
        path: Path to checkpoint file (e.g. best_model.pth).
        device: Device to map tensors onto.

    Returns:
        Full checkpoint dict (model_state_dict, model_name, etc.).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {path}")

    checkpoint = _torch.load(path, map_location=device, weights_only=False)

    state_dict = checkpoint.get("model_state_dict")
    if state_dict is None:
        raise KeyError("Checkpoint missing 'model_state_dict'")

    if isinstance(model, _torch.nn.DataParallel):
        model.module.load_state_dict(state_dict)
    else:
        model.load_state_dict(state_dict)

    _logger.info("Loaded checkpoint from %s", path)
    return checkpoint
