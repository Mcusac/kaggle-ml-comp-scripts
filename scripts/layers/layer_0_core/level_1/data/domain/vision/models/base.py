"""Base vision model abstract class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple, Union

from level_0 import get_nn_module_base_class, get_torch

torch = get_torch()
_NNModule = get_nn_module_base_class()


class BaseVisionModel(_NNModule, ABC):
    """
    Abstract base class for vision models.

    Defines the common interface all vision models must implement, ensuring
    they can be used interchangeably in the vision pipeline.

    All vision models must:
    - Support forward pass with single or dual (split) image inputs
    - Provide input size information
    - Support freezing/unfreezing backbone for transfer learning
    - Report whether pretrained weights were loaded
    """

    def __init__(self):
        """Initialize base model. Subclasses must call super().__init__()."""
        super().__init__()

    @abstractmethod
    def forward(
        self,
        x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]
    ) -> torch.Tensor:
        """
        Forward pass through the model.

        Args:
            x: Single tensor (B, C, H, W) or tuple of two tensors for split input.

        Returns:
            Output tensor of shape (B, num_classes).
        """
        ...

    @abstractmethod
    def get_input_size(self) -> Tuple[int, int]:
        """Return expected (height, width) input dimensions."""
        ...

    @abstractmethod
    def freeze_backbone(self) -> None:
        """Freeze backbone parameters (sets requires_grad=False)."""
        ...

    @abstractmethod
    def unfreeze_backbone(self) -> None:
        """Unfreeze backbone parameters (sets requires_grad=True)."""
        ...

    @abstractmethod
    def is_pretrained(self) -> bool:
        """Return True if pretrained weights were successfully loaded."""
        ...

    def save(self, path: str) -> None:
        """Save model state dict to path."""
        if torch is None:
            raise RuntimeError("PyTorch is required to save vision models.")
        torch.save(self.state_dict(), path)

    def load(self, path: str, device: str = 'cpu') -> None:
        """Load model state dict from path."""
        if torch is None:
            raise RuntimeError("PyTorch is required to load vision models.")
        state_dict = torch.load(path, map_location=device)
        self.load_state_dict(state_dict)

    def get_num_parameters(self) -> int:
        """Return total number of model parameters."""
        if torch is None:
            return 0
        return sum(p.numel() for p in self.parameters())