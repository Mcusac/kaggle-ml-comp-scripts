"""Base head for vision models (classification/regression)."""

from typing import Any, Optional

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()
_NNModule = torch.nn.Module if torch is not None else object
ModuleT = torch.nn.Module if torch is not None else Any
TensorT = torch.Tensor if torch is not None else Any


class BaseHead(_NNModule):
    """
    Base class for vision model heads.

    Provides common logic for building MLP heads with configurable
    activation, dropout, and optional hidden layer.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        hidden_size: Optional[int] = None,
        dropout: float = 0.3,
        activation: str = "relu",
    ):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features

        act_fn = self._get_activation(activation)

        if hidden_size is None or hidden_size <= 0:
            self.head = torch.nn.Linear(in_features, out_features)
        else:
            self.head = torch.nn.Sequential(
                torch.nn.Linear(in_features, hidden_size),
                act_fn,
                torch.nn.Dropout(dropout),
                torch.nn.Linear(hidden_size, out_features),
            )

    def _get_activation(self, activation: str) -> ModuleT:
        """Return activation module by name."""
        if torch is None:
            raise RuntimeError("PyTorch is required to build vision heads.")
        activation = activation.lower()
        if activation == "relu":
            return torch.nn.ReLU(inplace=True)
        if activation == "gelu":
            return torch.nn.GELU()
        if activation == "silu":
            return torch.nn.SiLU(inplace=True)
        raise ValueError(f"Unknown activation: {activation}")

    def forward(self, x: TensorT) -> TensorT:
        if torch is None:
            raise RuntimeError("PyTorch is required to run vision heads.")
        return self.head(x)


class ClassificationHead(BaseHead):
    """Classification head (semantic alias: num_classes -> out_features)."""

    def __init__(
        self,
        in_features: int,
        num_classes: int,
        hidden_size: Optional[int] = None,
        dropout: float = 0.3,
        activation: str = "relu",
    ):
        super().__init__(
            in_features,
            num_classes,
            hidden_size=hidden_size,
            dropout=dropout,
            activation=activation,
        )
        self.num_classes = self.out_features


class RegressionHead(BaseHead):
    """Regression head (uses out_features directly)."""

    pass
