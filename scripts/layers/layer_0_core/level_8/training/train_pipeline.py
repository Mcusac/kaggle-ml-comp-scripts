"""Atomic training pipeline for vision and tabular models."""

from pathlib import Path
from typing import Any, Dict

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_1 import BasePipeline, get_device, validate_config_section_exists
from layers.layer_0_core.level_2 import create_loss_function, create_optimizer, create_scheduler
from layers.layer_0_core.level_4 import create_dataloaders, create_vision_model, save_pickle
from layers.layer_0_core.level_5 import VisionTrainer
from layers.layer_0_core.level_7 import create_tabular_model

_logger = get_logger(__name__)


class TrainPipeline(BasePipeline):
    """
    Atomic pipeline for training models.

    Handles the complete training workflow:
    - Data loading
    - Model creation
    - Training execution
    - Checkpoint saving
    - Results tracking
    """

    def __init__(
        self,
        config: Any,
        model_type: str = 'vision',  # 'vision' or 'tabular'
        **kwargs
    ):
        super().__init__(config, **kwargs)
        self.model_type = model_type
        self.model = None
        self.trainer = None

    def setup(self) -> None:
        """Setup training pipeline."""
        _logger.info("🔧 Setting up training pipeline...")
        validate_config_section_exists(self.config, 'training')
        validate_config_section_exists(self.config, 'paths')
        if hasattr(self.config.paths, 'output_dir'):
            output_dir = Path(self.config.paths.output_dir)
            ensure_dir(output_dir)
            ensure_dir(output_dir / 'checkpoints')
            ensure_dir(output_dir / 'logs')
        _logger.info("✅ Training pipeline setup complete")

    def execute(self) -> Dict[str, Any]:
        """Execute training pipeline."""
        _logger.info("🏋️ Starting model training...")
        if self.model_type == 'vision':
            return self._train_vision()
        elif self.model_type == 'tabular':
            return self._train_tabular()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def _train_vision(self) -> Dict[str, Any]:
        """Train vision model."""
        device = get_device(self.config.device if hasattr(self.config, 'device') else 'auto')
        _logger.info(f"Creating vision model: {self.config.model.name}")
        self.model = create_vision_model(
            model_name=self.config.model.name,
            num_classes=self.config.model.num_classes,
            pretrained=self.config.model.pretrained
        )
        train_loader, val_loader = create_dataloaders(
            train_data=self.kwargs.get('train_data'),
            val_data=self.kwargs.get('val_data'),
            image_dir=self.kwargs.get('image_dir'),
            target_cols=self.kwargs.get('target_cols'),
            image_size=self.config.data.image_size if hasattr(self.config.data, 'image_size') else 224,
            batch_size=self.config.training.batch_size,
            augmentation=self.config.data.augmentation if hasattr(self.config.data, 'augmentation') else 'medium'
        )
        criterion = create_loss_function(
            self.config.training.loss_function if hasattr(self.config.training, 'loss_function') else 'mse'
        )
        optimizer = create_optimizer(
            self.model,
            optimizer_type=self.config.training.optimizer if hasattr(self.config.training, 'optimizer') else 'AdamW',
            learning_rate=self.config.training.learning_rate,
            weight_decay=self.config.training.weight_decay if hasattr(self.config.training, 'weight_decay') else 1e-2
        )
        scheduler = create_scheduler(
            optimizer,
            scheduler_type=self.config.training.scheduler if hasattr(self.config.training, 'scheduler') else 'None',
            num_epochs=self.config.training.num_epochs
        )
        self.trainer = VisionTrainer(
            model=self.model,
            criterion=criterion,
            optimizer=optimizer,
            device=device,
            scheduler=scheduler,
            use_mixed_precision=self.config.training.use_mixed_precision if hasattr(self.config.training, 'use_mixed_precision') else False
        )
        checkpoint_dir = self.kwargs.get('checkpoint_dir', str(Path(self.config.paths.output_dir) / 'checkpoints'))
        history = self.trainer.fit(
            train_loader=train_loader,
            val_loader=val_loader,
            num_epochs=self.config.training.num_epochs,
            early_stopping_patience=self.config.training.early_stopping_patience if hasattr(self.config.training, 'early_stopping_patience') else None,
            checkpoint_dir=checkpoint_dir
        )
        model_path = Path(checkpoint_dir) / 'final_model.pth'
        self.trainer.save_checkpoint(str(model_path))
        _logger.info(f"✅ Training complete. Model saved to {model_path}")
        return {
            'success': True,
            'model_path': str(model_path),
            'metrics': {'best_score': history['best_score'], 'best_epoch': history['best_epoch']},
            'history': history['history']
        }

    def _train_tabular(self) -> Dict[str, Any]:
        """Train tabular model."""
        X_train = self.kwargs.get('X_train')
        y_train = self.kwargs.get('y_train')
        if X_train is None or y_train is None:
            raise ValueError("X_train and y_train are required for tabular training")
        _logger.info(f"Creating tabular model: {self.config.model.type}")
        self.model = create_tabular_model(
            model_type=self.config.model.type,
            input_dim=X_train.shape[1],
            output_dim=y_train.shape[1] if y_train.ndim > 1 else 1,
            **self.config.model.hyperparameters if hasattr(self.config.model, 'hyperparameters') else {}
        )
        self.model.fit(X_train, y_train, **self.kwargs.get('fit_kwargs', {}))
        model_path = Path(self.config.paths.output_dir) / 'model.pkl'
        if hasattr(self.model, 'save'):
            self.model.save(str(model_path))
        else:
            save_pickle(self.model, model_path)
        _logger.info(f"✅ Training complete. Model saved to {model_path}")
        return {'success': True, 'model_path': str(model_path), 'metrics': {}}

    def cleanup(self) -> None:
        """Cleanup training resources."""
        if self.model is not None and hasattr(self.model, 'cpu'):
            self.model.cpu()
        self.trainer = None
