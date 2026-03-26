"""Forward pass with optional AMP."""

from typing import Union, Tuple

from level_0 import get_torch

torch = get_torch()
nn = torch.nn if torch is not None else None


def forward_with_amp(
    model: nn.Module,
    inputs: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
    use_amp: bool = False
) -> torch.Tensor:
    """
    Forward pass through model with optional automatic mixed precision.

    Args:
        model: PyTorch model.
        inputs: Model inputs (single tensor or tuple of tensors for dual-input models).
        use_amp: Whether to use automatic mixed precision (FP16).

    Returns:
        Model outputs.
    """
    if use_amp:
        with torch.amp.autocast('cuda'):
            return model(inputs)
    return model(inputs)
