"""
Unified loss functions for tabular and vision models.

Includes both standard PyTorch losses and custom implementations.
"""

from abc import ABC, abstractmethod
from typing import Literal, Optional

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()
nn = torch.nn if torch is not None else None
F = torch.nn.functional if torch is not None else None
_BaseLoss = nn.Module if nn is not None else object

# =====================================================
# Type Definitions
# =====================================================

LossType = Literal[
    # Regression
    "mse", "mae", "l1", "huber", "smooth_l1",
    # Classification
    "bce", "focal", "weighted_bce",
    "sparse_bce", "label_smoothing",
]

# =====================================================
# Base Loss
# =====================================================


class BaseLoss(_BaseLoss, ABC):
    """
    Base class for custom loss functions.
    Enforces a consistent forward(inputs, targets) interface and optional reduction.
    """

    def __init__(self, reduction: str = "mean"):
        super().__init__()
        self.reduction = reduction

    @abstractmethod
    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor,
    ) -> torch.Tensor:
        """Compute loss. Subclasses must implement."""
        ...


class FocalLoss(BaseLoss):
    """
    Focal Loss for addressing class imbalance.

    Reference: Lin et al. "Focal Loss for Dense Object Detection" (2017)
    https://arxiv.org/abs/1708.02002
    """

    def __init__(
        self,
        alpha: Optional[float] = None,
        gamma: float = 2.0,
        reduction: str = "mean"
    ):
        """
        Initialize Focal Loss.

        Args:
            alpha: Weighting factor in range [0,1] to balance positive/negative examples.
                  None means no weighting (default).
            gamma: Focusing parameter for modulating loss. Higher values down-weight
                  easy examples more. Typical values: [0, 5], commonly 2.0.
            reduction: Specifies the reduction to apply: 'none' | 'mean' | 'sum'.
        """
        super().__init__(reduction=reduction)
        self.alpha = alpha
        self.gamma = gamma

    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculate focal loss.

        Args:
            inputs: Predictions (logits), shape (N, C) or (N,).
            targets: Ground truth labels, same shape as inputs.

        Returns:
            Focal loss value.
        """
        # Calculate BCE loss
        bce_loss = F.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )

        # Calculate probabilities
        probs = torch.sigmoid(inputs)

        # Calculate pt (probability of true class)
        pt = torch.where(targets == 1, probs, 1 - probs)

        # Calculate focal term: (1 - pt)^gamma
        focal_term = (1 - pt) ** self.gamma

        # Calculate focal loss
        loss = focal_term * bce_loss

        # Apply alpha weighting if specified
        if self.alpha is not None:
            alpha_t = torch.where(
                targets == 1,
                torch.tensor(self.alpha, device=targets.device),
                torch.tensor(1 - self.alpha, device=targets.device)
            )
            loss = alpha_t * loss

        # Apply reduction
        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        else:  # 'none'
            return loss


class WeightedBCELoss(BaseLoss):
    """
    Weighted Binary Cross-Entropy Loss.

    Applies per-class or per-sample weights to standard BCE loss.
    """

    def __init__(
        self,
        weights: Optional[torch.Tensor] = None,
        reduction: str = "mean"
    ):
        """
        Initialize Weighted BCE Loss.

        Args:
            weights: Class weights. Can be:
                    - None: No weighting (default)
                    - 1D tensor of shape (C,): Per-class weights
                    - 2D tensor same shape as targets: Per-sample weights
            reduction: Specifies the reduction to apply: 'none' | 'mean' | 'sum'.
        """
        super().__init__(reduction=reduction)
        self.weights = weights

    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculate weighted BCE loss.

        Args:
            inputs: Predictions (logits).
            targets: Ground truth labels.

        Returns:
            Weighted BCE loss value.
        """
        # Calculate base BCE loss
        loss = F.binary_cross_entropy_with_logits(
            inputs, targets, reduction='none'
        )

        # Apply weights if provided
        if self.weights is not None:
            if self.weights.dim() == 1:
                # Per-class weights: broadcast to match targets
                weights = self.weights.unsqueeze(0)
                loss = loss * weights
            else:
                # Per-sample weights: direct multiplication
                loss = loss * self.weights

        # Apply reduction
        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        else:  # 'none'
            return loss


class SparseBCEWithLogitsLoss(BaseLoss):
    """
    BCE Loss optimized for sparse multi-label classification.

    More memory-efficient for cases with many classes but few positive labels.
    """

    def __init__(self, pos_weight: Optional[torch.Tensor] = None, reduction: str = "mean"):
        """
        Initialize Sparse BCE Loss.

        Args:
            pos_weight: Weight for positive examples. Can be:
                       - None: No weighting (default)
                       - 1D tensor of shape (C,): Per-class positive weights
        """
        super().__init__(reduction=reduction)
        self.pos_weight = pos_weight

    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculate sparse BCE loss.

        Args:
            inputs: Predictions (logits), shape (N, C).
            targets: Sparse ground truth labels, shape (N, C).

        Returns:
            BCE loss value.
        """
        return F.binary_cross_entropy_with_logits(
            inputs,
            targets,
            pos_weight=self.pos_weight,
            reduction=self.reduction
        )


class LabelSmoothingBCEWithLogitsLoss(BaseLoss):
    """
    BCE Loss with Label Smoothing for regularization.

    Label smoothing prevents the model from becoming over-confident
    by smoothing the hard 0/1 targets.
    """

    def __init__(
        self,
        smoothing: float = 0.1,
        reduction: str = "mean"
    ):
        """
        Initialize Label Smoothing BCE Loss.

        Args:
            smoothing: Smoothing factor in range [0, 1].
                      0 = no smoothing (hard labels)
                      Higher values = more smoothing
                      Typical values: 0.05 - 0.2
            reduction: Specifies the reduction to apply: 'none' | 'mean' | 'sum'.
        """
        super().__init__(reduction=reduction)
        if not 0 <= smoothing < 1:
            raise ValueError(f"smoothing must be in [0, 1), got {smoothing}")

        self.smoothing = smoothing

    def forward(
        self,
        inputs: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """
        Calculate label smoothed BCE loss.

        Args:
            inputs: Predictions (logits).
            targets: Ground truth labels (0 or 1).

        Returns:
            Label smoothed BCE loss value.
        """
        # Apply label smoothing
        # Transform hard 0/1 labels to soft labels
        # 0 -> smoothing/2
        # 1 -> 1 - smoothing/2
        targets_smooth = targets * (1 - self.smoothing) + self.smoothing / 2

        # Calculate BCE loss with smoothed targets
        loss = F.binary_cross_entropy_with_logits(
            inputs, targets_smooth, reduction=self.reduction
        )

        return loss