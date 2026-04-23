"""Training phase executor for BaseModelTrainer."""

from typing import Any, Tuple

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import train_one_epoch, run_supervised_batch

_torch = get_torch()
_nn = _torch.nn
_DataLoader = _torch.utils.data.DataLoader
_logger = get_logger(__name__)


class TrainingPhaseExecutor:
    """Executes the training phase of a supervised training loop."""

    def __init__(
        self,
        model: _nn.Module,
        device: _torch.device,
        criterion: _nn.Module,
        optimizer: _torch.optim.Optimizer,
        scheduler: Any,
        use_mixed_precision: bool,
        scaler: Any,
    ):
        self.model = model
        self.device = device
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.use_mixed_precision = use_mixed_precision
        self.scaler = scaler

    def process_batch(
        self,
        batch: Tuple,
    ) -> Tuple[_torch.Tensor, _torch.Tensor, _torch.Tensor]:
        """Process a single batch via run_supervised_batch."""
        return run_supervised_batch(self.model, self.device, self.criterion, batch)

    def _make_batch_processor(self):
        """Return a callable(batch) -> loss for train_one_epoch."""
        def process(batch):
            if self.use_mixed_precision and self.scaler:
                with _torch.amp.autocast('cuda'):
                    _, _, loss = self.process_batch(batch)
            else:
                _, _, loss = self.process_batch(batch)
            return loss
        return process

    def train_epoch(self, train_loader: _DataLoader) -> float:
        """Train for one epoch and return average training loss."""
        self.model.train()
        return train_one_epoch(
            train_loader,
            batch_processor=self._make_batch_processor(),
            optimizer=self.optimizer,
            scaler=self.scaler,
        )