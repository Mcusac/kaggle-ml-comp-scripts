"""Checkpoint saving utilities with DataParallel handling."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from level_0 import ensure_dir, get_logger, get_torch

torch = get_torch()
nn = torch.nn if torch is not None else None
optim = torch.optim if torch is not None else None
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _strip_module_prefix(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Remove the 'module.' prefix added by DataParallel from all state dict keys.

    When a model is saved while wrapped in DataParallel every key is prefixed
    with 'module.'. This helper produces a clean state dict that can be loaded
    into either a wrapped or unwrapped model.

    Args:
        state_dict: Model state dict, possibly with 'module.' prefixed keys.

    Returns:
        State dict with 'module.' prefix removed from all keys.
        If no keys have the prefix the original dict is returned unchanged.
    """
    if not any(k.startswith("module.") for k in state_dict):
        return state_dict
    return {k.removeprefix("module."): v for k, v in state_dict.items()}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_checkpoint(
    model: nn.Module,
    optimizer: optim.Optimizer,
    scheduler: Optional[optim.lr_scheduler._LRScheduler],
    path: Path,
    epoch: int,
    best_score: float,
    history: List[Dict[str, Any]],
) -> None:
    """Save a training checkpoint.

    Saves the underlying model state without the 'module.' prefix so the
    checkpoint is compatible with both DataParallel and non-parallel models.

    Args:
        model: PyTorch model (may be wrapped in DataParallel).
        optimizer: Optimizer whose state should be saved.
        scheduler: Optional scheduler whose state should be saved.
        path: Destination file path.
        epoch: Current epoch number.
        best_score: Best validation score achieved so far.
        history: List of per-epoch history dicts.
    """
    raw_state = (
        model.module.state_dict()
        if isinstance(model, nn.DataParallel)
        else model.state_dict()
    )
    # Always save without the prefix so checkpoints are portable.
    model_state_dict = _strip_module_prefix(raw_state)

    checkpoint: Dict[str, Any] = {
        "epoch": epoch,
        "model_state_dict": model_state_dict,
        "optimizer_state_dict": optimizer.state_dict(),
        "best_score": best_score,
        "history": history,
    }

    if scheduler is not None:
        checkpoint["scheduler_state_dict"] = scheduler.state_dict()

    path = Path(path)
    ensure_dir(path.parent)
    torch.save(checkpoint, path)
    logger.debug("Saved checkpoint to %s", path)


def load_model_checkpoint(
    checkpoint_path: Path,
    model: torch.nn.Module,
    optimizer: Optional[torch.optim.Optimizer] = None,
    scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
    device: Optional[torch.device] = None,
) -> Dict[str, Any]:
    """Load a training checkpoint into a model.

    Handles both DataParallel-wrapped and plain models. The 'module.' prefix
    is stripped before loading so that checkpoints saved from either model
    variant can be loaded into either variant.

    Args:
        checkpoint_path: Path to the checkpoint file.
        model: Model to load weights into (may be wrapped in DataParallel).
        optimizer: Optional optimizer to restore state into.
        scheduler: Optional scheduler to restore state into.
        device: Device to map the checkpoint tensors onto.

    Returns:
        Full checkpoint dict (epoch, best_score, history, etc.).

    Raises:
        FileNotFoundError: If checkpoint_path does not exist.
    """
    checkpoint_path = Path(checkpoint_path)
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)

    state_dict = _strip_module_prefix(checkpoint["model_state_dict"])

    target = model.module if isinstance(model, torch.nn.DataParallel) else model
    target.load_state_dict(state_dict)

    if optimizer is not None and "optimizer_state_dict" in checkpoint:
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

    if (
        scheduler is not None
        and "scheduler_state_dict" in checkpoint
        and checkpoint["scheduler_state_dict"] is not None
    ):
        scheduler.load_state_dict(checkpoint["scheduler_state_dict"])

    logger.info("Loaded checkpoint from %s", checkpoint_path)
    return checkpoint