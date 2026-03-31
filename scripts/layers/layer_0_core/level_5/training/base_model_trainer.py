"""End-to-end model trainer with early stopping and checkpointing."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch
from layers.layer_0_core.level_1 import get_device, setup_mixed_precision
from layers.layer_0_core.level_2 import (
    extract_config_settings, 
    get_training_config_value,
    create_optimizer,
    create_scheduler,
    create_loss_function,
    finalize_epoch,
    ModelCheckpointer,

    TrainingPhaseExecutor,
    ValidationPhaseExecutor,
)
from layers.layer_0_core.level_4 import create_vision_model

logger = get_logger(__name__)
torch = get_torch()
nn = torch.nn
DataLoader = torch.utils.data.DataLoader


class BaseModelTrainer:
    """
    End-to-end model trainer.

    Owns the full training loop: epoch execution, validation, learning rate
    scheduling, checkpointing, and early stopping. Delegates each concern to
    a focused helper or builder rather than implementing it directly.
    """

    def __init__(
        self,
        config: Union[Any, Dict[str, Any]],
        device: Optional[Any] = None,
        model: Optional[Any] = None,
        model_name: Optional[str] = None,
        num_primary_targets: Optional[int] = None,
        image_size: Optional[Tuple[int, int]] = None,
        dataset_type: str = 'split',
        metric_calculator: Optional[Any] = None,
    ):
        """
        Initialise trainer.

        Args:
            config: Configuration object or dict with training settings.
            device: Target device (default: auto-detect).
            model: Pre-built model. If None, creates one from model_name.
            model_name: Model identifier used when model is None.
            num_primary_targets: Output dimension override; falls back to config.
            image_size: (height, width) override; falls back to config.
            dataset_type: Batch format expected by helpers ('split' or 'full').
            metric_calculator: Callable injected into ValidationPhaseExecutor.
        """
        self.device = device if device is not None else get_device('auto')
        self.config = config
        self.dataset_type = dataset_type

        self.num_primary_targets, self.model_name, self.image_size = extract_config_settings(
            config, num_primary_targets, model_name, image_size
        )

        self.model = self._build_model(model)
        self.criterion, self.optimizer, self.scheduler = self._build_criterion_optimizer_scheduler()
        self.use_mixed_precision, self.scaler = setup_mixed_precision(config, self.device)
        self.training_helper, self.validation_helper, self.checkpoint_helper = (
            self._build_phase_helpers(metric_calculator)
        )

        self.history: List[Dict] = []
        self.best_score: float = -float('inf')
        self.best_epoch: int = 0

    # ------------------------------------------------------------------
    # Builders — called once during __init__
    # ------------------------------------------------------------------

    def _build_model(self, model: Optional[Any]) -> Any:
        """Create or accept a model, place it on device, and apply multi-GPU if configured."""
        if model is None:
            model = create_vision_model(
                model_name=self.model_name,
                num_classes=self.num_primary_targets or 3,
                image_size=self.image_size,
                pretrained=True,
            )
        model = model.to(self.device)
        model = self._apply_multi_gpu(model)
        logger.info(f"Model ready: {self.model_name}")
        if self.image_size:
            logger.info(f"Input size: {self.image_size}")
        return model

    def _apply_multi_gpu(self, model: Any) -> Any:
        """Wrap model in DataParallel when multi-GPU is enabled in config."""
        use_multi_gpu = False
        if hasattr(self.config, 'device'):
            use_multi_gpu = getattr(self.config.device, 'use_multi_gpu', False)
        elif isinstance(self.config, dict):
            use_multi_gpu = self.config.get('use_multi_gpu', False)

        if use_multi_gpu and self.device.type == 'cuda' and torch.cuda.device_count() > 1:
            model = nn.DataParallel(model)
            logger.info(f"DataParallel enabled across {torch.cuda.device_count()} GPUs")
        return model

    def _build_criterion_optimizer_scheduler(self) -> Tuple[Any, Any, Any]:
        """Instantiate loss function, optimizer, and learning rate scheduler from config."""
        criterion = create_loss_function(self.config)
        optimizer = create_optimizer(self.model, self.config)
        scheduler = create_scheduler(optimizer, self.config)
        return criterion, optimizer, scheduler

    def _build_phase_helpers(self, metric_calculator: Optional[Any]) -> Tuple[Any, Any, Any]:
        """Instantiate training, validation, and checkpoint helpers."""
        training_helper = TrainingPhaseExecutor(
            self.model, self.device, self.criterion, self.optimizer,
            self.scheduler, self.use_mixed_precision, self.scaler,
        )
        validation_helper = ValidationPhaseExecutor(
            self.model, self.device, self.criterion, self.config,
            metric_calculator=metric_calculator,
        )
        checkpoint_helper = ModelCheckpointer(
            self.model, self.optimizer, self.scheduler, self.device,
        )
        return training_helper, validation_helper, checkpoint_helper

    # ------------------------------------------------------------------
    # Public single-step interface
    # ------------------------------------------------------------------

    def train_epoch(self, train_loader: DataLoader) -> float:
        """Run one training pass. Returns mean training loss."""
        return self.training_helper.train_epoch(train_loader)

    def validate(self, val_loader: DataLoader) -> Tuple[float, float, Any]:
        """Run one validation pass. Returns (val_loss, metric_value, per_target_scores)."""
        return self.validation_helper.validate(val_loader)

    # ------------------------------------------------------------------
    # Private epoch helpers
    # ------------------------------------------------------------------

    def _run_epoch(
        self,
        epoch: int,
        num_epochs: int,
        train_loader: DataLoader,
        val_loader: DataLoader,
    ) -> Tuple[float, float, float]:
        """
        Execute one full epoch: train, validate, step scheduler, log, record history.

        Returns:
            (train_loss, val_loss, metric_value)
        """
        train_loss = self.train_epoch(train_loader)
        val_loss, metric_value, per_target_scores = self.validate(val_loader)

        history_entry = finalize_epoch(
            epoch=epoch,
            num_epochs=num_epochs,
            train_loss=train_loss,
            val_loss=val_loss,
            metric_name='weighted_r2',
            metric_value=metric_value,
            per_target_scores=per_target_scores,
            config=self.config,
            scheduler=self.scheduler,
            optimizer=self.optimizer,
        )
        self.history.append(history_entry)

        return train_loss, val_loss, metric_value

    def _save_if_best(
        self,
        epoch: int,
        metric: float,
        save_dir: Optional[Path],
    ) -> bool:
        """
        Update best state and save checkpoint when metric improves.

        Args:
            epoch: Current epoch index.
            metric: Metric value to compare against current best.
            save_dir: Directory to write checkpoint to, or None to skip saving.

        Returns:
            True if metric improved, False otherwise.
        """
        if metric <= self.best_score:
            return False
        self.best_score = metric
        self.best_epoch = epoch
        if save_dir:
            self.checkpoint_helper.save_best_model(
                epoch, self.best_score, self.history, save_dir
            )
        return True

    # ------------------------------------------------------------------
    # Full training loop
    # ------------------------------------------------------------------

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        num_epochs: Optional[int] = None,
        save_dir: Optional[Union[str, Path]] = None,
        resume: bool = True,
        early_stopping_patience: Optional[int] = None,
    ) -> List[Dict]:
        """
        Train with early stopping.

        Args:
            train_loader: DataLoader for training data.
            val_loader: DataLoader for validation data.
            num_epochs: Total epochs (default: from config or 100).
            save_dir: Directory for checkpoints. No checkpointing if None.
            resume: Resume from existing checkpoint when save_dir is set.
            early_stopping_patience: Epochs without improvement before stopping
                                     (default: from config or 10).

        Returns:
            Training history as a list of per-epoch dicts.
        """
        num_epochs = num_epochs or get_training_config_value(self.config, 'num_epochs', 100)
        patience = early_stopping_patience or get_training_config_value(
            self.config, 'early_stopping_patience', 10
        )

        save_dir_path = Path(save_dir) if save_dir else None
        if save_dir_path:
            ensure_dir(save_dir_path)

        start_epoch = 0
        if resume and save_dir_path:
            resume_info = self.checkpoint_helper.resume_from_checkpoint(save_dir_path, num_epochs)
            start_epoch = resume_info['start_epoch']
            self.best_score = resume_info['best_score']
            self.history = resume_info['history']

        epochs_without_improvement = 0
        logger.info(f"Training for {num_epochs} epochs from epoch {start_epoch}")

        try:
            for epoch in range(start_epoch, num_epochs):
                _, _, metric = self._run_epoch(epoch, num_epochs, train_loader, val_loader)

                if self._save_if_best(epoch, metric, save_dir_path):
                    epochs_without_improvement = 0
                else:
                    epochs_without_improvement += 1

                if epochs_without_improvement >= patience:
                    logger.info(f"Early stopping after {patience} epochs without improvement")
                    break

        except KeyboardInterrupt:
            logger.info("Training interrupted by user")
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

        logger.info(
            f"Training complete. Best weighted R²: {self.best_score:.4f} at epoch {self.best_epoch}"
        )
        return self.history