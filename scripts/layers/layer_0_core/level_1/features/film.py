"""FiLM (Feature-wise Linear Modulation) fusion module."""

from __future__ import annotations

from layers.layer_0_core.level_0 import get_logger, get_nn_module_base_class, get_torch

torch = get_torch()
_NNModule = get_nn_module_base_class()
logger = get_logger(__name__)


class FiLM(_NNModule):
    """
    FiLM (Feature-wise Linear Modulation) module.

    Generates gamma (scale) and beta (shift) parameters from context features
    to modulate other features: feat_mod = feat * (1 + gamma) + beta
    """

    def __init__(self, feat_dim: int):
        """
        Initialize FiLM module.

        Args:
            feat_dim: Feature dimension (input and output dimension)
        """
        super().__init__()
        if torch is None:
            raise RuntimeError("PyTorch is required for FiLM.")
        self.feat_dim = feat_dim

        # MLP that generates gamma and beta from context
        # Output is 2 * feat_dim (gamma + beta concatenated)
        self.mlp = torch.nn.Sequential(
            torch.nn.Linear(feat_dim, feat_dim // 2),
            torch.nn.ReLU(inplace=True),
            torch.nn.Linear(feat_dim // 2, feat_dim * 2)
        )

    def forward(self, context: torch.Tensor) -> tuple:
        """
        Generate gamma and beta from context features.

        Args:
            context: Context features of shape (B, feat_dim)

        Returns:
            Tuple of (gamma, beta), each of shape (B, feat_dim)
        """
        # Generate gamma and beta (concatenated)
        gamma_beta = self.mlp(context)  # (B, feat_dim * 2)

        # Split into gamma and beta
        gamma, beta = torch.chunk(gamma_beta, 2, dim=1)  # Each: (B, feat_dim)

        return gamma, beta
