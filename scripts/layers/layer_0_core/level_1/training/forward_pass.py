"""Forward pass with optional AMP."""

from typing import Union, Tuple

from layers.layer_0_core.level_0 import get_torch

_torch = get_torch()
_nn = _torch.nn if _torch is not None else None


def forward_with_amp(
    model: _nn.Module,
    inputs: Union[_torch.Tensor, Tuple[_torch.Tensor, _torch.Tensor]],
    use_amp: bool = False
) -> _torch.Tensor:
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
        with _torch.amp.autocast('cuda'):
            return model(inputs)
    return model(inputs)
