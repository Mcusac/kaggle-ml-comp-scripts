"""Validation phase executor for BaseModelTrainer."""

import numpy as np

from typing import Any, Callable, List, Tuple

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import run_supervised_batch

_torch = get_torch()
_nn = _torch.nn
_DataLoader = _torch.utils.data.DataLoader
_logger = get_logger(__name__)


class ValidationPhaseExecutor:
    """Executes the validation phase of a supervised training loop."""

    def __init__(
        self,
        model: _nn.Module,
        device: _torch.device,
        criterion: _nn.Module,
        config: Any,
        metric_calculator: Callable,
    ):
        """
        Args:
            model: PyTorch model.
            device: Validation device.
            criterion: Loss function.
            config: Configuration object.
            metric_calculator: Callable(predictions, targets, config=)
                               -> (weighted_r2, r2_scores). Injected from
                               contest context.
        """
        self.model = model
        self.device = device
        self.criterion = criterion
        self.config = config
        self.metric_calculator = metric_calculator

    def process_batch(
        self,
        batch: Tuple,
    ) -> Tuple[_torch.Tensor, _torch.Tensor, _torch.Tensor]:
        """Process a single batch via run_supervised_batch."""
        return run_supervised_batch(self.model, self.device, self.criterion, batch)

    def validate(self, val_loader: _DataLoader) -> Tuple[float, float, np.ndarray]:
        """
        Validate model on validation set.

        Args:
            val_loader: Validation DataLoader.

        Returns:
            Tuple of (val_loss, weighted_r2, r2_scores_per_target).

        Raises:
            ValueError: If val_loader is empty or yields no batches.
        """
        if len(val_loader) == 0:
            raise ValueError("val_loader cannot be empty")

        self.model.eval()
        total_loss = 0.0
        all_outputs: List[np.ndarray] = []
        all_targets: List[np.ndarray] = []
        num_batches = 0

        with _torch.no_grad():
            for batch in val_loader:
                outputs, targets, loss = self.process_batch(batch)

                if _torch.isnan(loss):
                    _logger.warning("NaN loss detected during validation")

                total_loss += loss.item()
                num_batches += 1
                all_outputs.append(outputs.detach().cpu().numpy())
                all_targets.append(targets.detach().cpu().numpy())

        if num_batches == 0:
            raise ValueError("No batches processed in validate")

        outputs = np.concatenate(all_outputs, axis=0)
        targets = np.concatenate(all_targets, axis=0)
        weighted_r2, r2_scores = self.metric_calculator(outputs, targets, config=self.config)
        return total_loss / num_batches, weighted_r2, r2_scores