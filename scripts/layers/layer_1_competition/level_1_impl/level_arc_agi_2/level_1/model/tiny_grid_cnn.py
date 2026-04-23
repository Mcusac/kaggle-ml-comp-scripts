"""Small conv model: per-cell class logits on a padded canvas."""

import torch.nn as nn

from layers.layer_0_core.level_0 import get_torch

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import NUM_CHANNELS

_torch = get_torch()


class TinyGridCNN(nn.Module):
    """Maps one-hot input grid to class logits (same spatial resolution)."""

    def __init__(self, num_classes: int = NUM_CHANNELS, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(NUM_CHANNELS, hidden, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden, hidden, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden, num_classes, kernel_size=1),
        )

    def forward(self, x: _torch.Tensor) -> _torch.Tensor:
        return self.net(x)
