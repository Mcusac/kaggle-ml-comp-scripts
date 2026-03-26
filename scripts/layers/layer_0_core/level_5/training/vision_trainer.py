"""Main vision model trainer. Uses level_0, level_1, level_5."""

import numpy as np

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch, extract_batch_data
from layers.layer_0_core.level_1 import train_one_epoch, load_model_checkpoint, forward_with_amp
from level_4 import calculate_metrics

logger = get_logger(__name__)
torch = get_torch()
nn = torch.nn
DataLoader = torch.utils.data.DataLoader


class VisionTrainer:
    """
    Vision model trainer with training/validation loops and early stopping.

    Handles model training with early stopping, checkpoint saving/loading,
    learning rate scheduling, and metric calculation. Supports mixed precision
    training for memory efficiency.
    """

    def __init__(
        self,
        model: nn.Module,
        criterion: nn.Module,
        optimizer: torch.optim.Optimizer,
        device: torch.device,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None,
        use_mixed_precision: bool = False,
    ):
        """Initialize Vision Trainer."""
        self.model = model.to(device)
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device
        self.scheduler = scheduler
        self.use_mixed_precision = use_mixed_precision

        self.scaler = None
        if self.use_mixed_precision:
            self.scaler = torch.cuda.amp.GradScaler()
            logger.info("✅ Mixed precision (FP16) training enabled")

        self.history: List[Dict] = []
        self.best_score = -float("inf")
        self.best_epoch = 0
        self.epochs_no_improve = 0

    def _make_batch_processor(self):
        """Return a callable(batch) -> loss for train_one_epoch."""

        def process(batch):
            images, targets = extract_batch_data(batch, self.device)
            if targets is None:
                raise ValueError("Targets are required for training")
            outputs = forward_with_amp(self.model, images, self.use_mixed_precision)
            return self.criterion(outputs, targets)

        return process

    def train_epoch(self, train_loader: DataLoader, epoch: int) -> float:
        """Train for one epoch."""
        self.model.train()
        return train_one_epoch(
            train_loader,
            batch_processor=self._make_batch_processor(),
            optimizer=self.optimizer,
            scaler=self.scaler,
            use_tqdm=True,
            tqdm_desc=f"Epoch {epoch} [Train]",
        )

    @torch.no_grad()
    def validate(
        self,
        val_loader: DataLoader,
        epoch: int,
    ) -> Tuple[float, Optional[float]]:
        """Validate the model."""
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_targets = []
        num_batches = 0

        pbar = tqdm(val_loader, desc=f"Epoch {epoch} [Val]")

        for batch in pbar:
            images, targets = extract_batch_data(batch, self.device)

            outputs = forward_with_amp(self.model, images, self.use_mixed_precision)

            if targets is not None:
                loss = self.criterion(outputs, targets)
                total_loss += loss.item()

                all_preds.append(outputs.cpu().numpy())
                all_targets.append(targets.cpu().numpy())

            num_batches += 1

            if targets is not None:
                pbar.set_postfix({"loss": f"{loss.item():.4f}"})

        avg_loss = total_loss / num_batches if num_batches > 0 else 0.0

        metric_value = None
        if all_preds and all_targets:
            all_preds = np.concatenate(all_preds, axis=0)
            all_targets = np.concatenate(all_targets, axis=0)
            metric_value = calculate_metrics("classification", all_targets, all_preds)

        return avg_loss, metric_value

    def fit(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_epochs: int,
        early_stopping_patience: Optional[int] = None,
        checkpoint_dir: Optional[str] = None,
        verbose: bool = True,
    ) -> Dict:
        """Train the model for multiple epochs."""
        if checkpoint_dir:
            checkpoint_path = Path(checkpoint_dir)
            ensure_dir(checkpoint_path)

        for epoch in range(1, num_epochs + 1):
            train_loss = self.train_epoch(train_loader, epoch)

            val_loss, val_metric = self.validate(val_loader, epoch)

            if self.scheduler:
                if isinstance(self.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                    metric_for_scheduler = val_metric if val_metric is not None else val_loss
                    self.scheduler.step(metric_for_scheduler)
                else:
                    self.scheduler.step()

            current_lr = self.optimizer.param_groups[0]["lr"]

            epoch_history = {
                "epoch": epoch,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "val_metric": val_metric,
                "lr": current_lr,
            }
            self.history.append(epoch_history)

            if verbose:
                log_str = f"Epoch {epoch}/{num_epochs} - "
                log_str += f"train_loss: {train_loss:.4f}, val_loss: {val_loss:.4f}"
                if val_metric is not None:
                    log_str += f", val_metric: {val_metric:.4f}"
                log_str += f", lr: {current_lr:.2e}"
                logger.info(log_str)

            score = val_metric if val_metric is not None else -val_loss

            if score > self.best_score:
                self.best_score = score
                self.best_epoch = epoch
                self.epochs_no_improve = 0

                if checkpoint_dir:
                    best_checkpoint_path = checkpoint_path / "best_model.pth"
                    self.save_checkpoint(best_checkpoint_path)
                    if verbose:
                        logger.info(f"✅ Saved best model (score: {score:.4f})")
            else:
                self.epochs_no_improve += 1

            if early_stopping_patience and self.epochs_no_improve >= early_stopping_patience:
                logger.info(f"⚠️ Early stopping triggered after {epoch} epochs")
                logger.info(f"  Best score: {self.best_score:.4f} at epoch {self.best_epoch}")
                break

        logger.info("🎉 Training complete!")
        logger.info(f"  Best score: {self.best_score:.4f} at epoch {self.best_epoch}")

        return {
            "history": self.history,
            "best_score": self.best_score,
            "best_epoch": self.best_epoch,
        }

    def save_checkpoint(self, path) -> None:
        """Save model checkpoint."""
        torch.save(
            {
                "model_state_dict": self.model.state_dict(),
                "optimizer_state_dict": self.optimizer.state_dict(),
                "scheduler_state_dict": self.scheduler.state_dict() if self.scheduler else None,
                "best_score": self.best_score,
                "best_epoch": self.best_epoch,
                "history": self.history,
            },
            path,
        )

    def load_checkpoint(self, path: str) -> None:
        """Load model checkpoint."""
        checkpoint = load_model_checkpoint(
            Path(path),
            model=self.model,
            optimizer=self.optimizer,
            scheduler=self.scheduler,
            device=self.device,
        )
        self.best_score = checkpoint.get("best_score", -float("inf"))
        self.best_epoch = checkpoint.get("best_epoch", checkpoint.get("epoch", 0))
        self.history = checkpoint.get("history", [])
        logger.info(f"  Best score: {self.best_score:.4f} at epoch {self.best_epoch}")
