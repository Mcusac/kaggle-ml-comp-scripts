"""
Model input/output utilities.

Framework layer: generic model persistence helpers.
"""

import json
import pickle
from pathlib import Path
from typing import Any

from level_0 import ensure_dir, get_torch

# ------------------------------------------------------------------
# Save
# ------------------------------------------------------------------

def save_regression_model(
    model: Any,
    save_dir: Path,
) -> None:
    """
    Save trained regression model and metadata.

    Args:
        model: Trained regression model.
        save_dir: Directory to save model to.
    """

    ensure_dir(save_dir)

    # Save model
    model_path = save_dir / "regression_model.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    # Save metadata
    metadata = {
        "model_type": type(model).__name__,
        "model_path": str(model_path),
    }

    metadata_path = save_dir / "metadata.json"

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)


def save_vision_model(model: Any, path: str) -> None:
    """
    Save a vision model's state dict to path.

    Args:
        model: PyTorch model whose state dict should be saved.
        path: Destination file path (e.g. 'checkpoints/best_model.pth').
    """
    torch = get_torch()
    ensure_dir(Path(path).parent)
    torch.save(model.state_dict(), path)

# ------------------------------------------------------------------
# Load
# ------------------------------------------------------------------


def load_vision_model(model: Any, path: str, device: str = "cpu") -> None:
    """
    Load a vision model's state dict from path into model in-place.

    Args:
        model: PyTorch model to load weights into.
        path: Source file path.
        device: Device to map tensors onto (default: 'cpu').

    Raises:
        FileNotFoundError: If path does not exist.
    """
    torch = get_torch()
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Model state dict not found: {path}")
    state_dict = torch.load(path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)