"""Model checkpointer for BaseModelTrainer."""

from pathlib import Path
from typing import Dict, Any, List

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import load_model_checkpoint

torch = get_torch()
nn = torch.nn
logger = get_logger(__name__)


class ModelCheckpointer:
    """Saves and loads model checkpoints during training."""

    def __init__(
        self,
        model: nn.Module,
        optimizer,
        scheduler,
        device: torch.device,
    ):
        """
        Args:
            model: PyTorch model.
            optimizer: Optimizer.
            scheduler: Learning rate scheduler.
            device: Training device.
        """
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device

    def resume_from_checkpoint(
        self,
        save_dir: Path,
        num_epochs: int,
    ) -> Dict[str, Any]:
        """
        Resume training from checkpoint if one exists.

        Args:
            save_dir: Directory containing the checkpoint file.
            num_epochs: Total number of epochs planned.

        Returns:
            Dict with keys: start_epoch, best_score, history.
        """
        checkpoint_path = save_dir / 'best_model.pth'
        if not checkpoint_path.exists():
            return {'start_epoch': 0, 'best_score': -float('inf'), 'history': []}

        logger.info(f"Found existing checkpoint at {checkpoint_path}")
        logger.info("Resuming training from checkpoint...")
        try:
            checkpoint_meta = load_model_checkpoint(
                checkpoint_path,
                model=self.model,
                optimizer=self.optimizer,
                scheduler=self.scheduler,
                device=self.device,
            )
            best_score = checkpoint_meta.get('best_score', -float('inf'))
            history = checkpoint_meta.get('history', [])
            start_epoch = checkpoint_meta.get('epoch', 0)
            logger.info(f"Resuming from epoch {start_epoch}/{num_epochs}")
            logger.info(f"Best score so far: {best_score:.4f}")
            return {'start_epoch': start_epoch, 'best_score': best_score, 'history': history}
        except (RuntimeError, EOFError, OSError, FileNotFoundError) as e:
            logger.warning(f"Failed to load checkpoint from {checkpoint_path}: {e}")
            logger.warning("Checkpoint corrupted or incompatible — starting fresh.")
            try:
                checkpoint_path.unlink()
                logger.info(f"Deleted corrupted checkpoint: {checkpoint_path}")
            except Exception as cleanup_error:
                logger.warning(f"Could not delete corrupted checkpoint: {cleanup_error}")
            return {'start_epoch': 0, 'best_score': -float('inf'), 'history': []}

    def _build_checkpoint_dict(
        self,
        epoch: int,
        best_score: float,
        history: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Assemble the checkpoint dict from current model and optimizer state."""
        model_state = (
            self.model.module.state_dict()
            if isinstance(self.model, nn.DataParallel)
            else self.model.state_dict()
        )
        return {
            'epoch': epoch,
            'model_state_dict': model_state,
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'best_score': best_score,
            'history': history,
        }

    def save_best_model(
        self,
        epoch: int,
        best_score: float,
        history: List[Dict[str, Any]],
        save_dir: Path,
    ) -> None:
        """
        Save the best model checkpoint to disk.

        Args:
            epoch: Current epoch number.
            best_score: Best score achieved so far.
            history: Training history entries.
            save_dir: Directory to write the checkpoint into.
        """
        checkpoint_path = save_dir / 'best_model.pth'
        checkpoint = self._build_checkpoint_dict(epoch, best_score, history)
        torch.save(checkpoint, checkpoint_path, _use_new_zipfile_serialization=False)
        logger.info(f"Saved best model (R²={best_score:.4f}) to {checkpoint_path}")