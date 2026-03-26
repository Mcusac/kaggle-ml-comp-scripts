"""Train a single CV fold: trainer, dataloaders, and train loop."""

from pathlib import Path
from typing import Any, Tuple

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_1 import cleanup_gpu_memory, get_device
from layers.layer_0_core.level_3 import (
    create_train_dataloader,
    create_val_dataloader,
)
from layers.layer_1_competition.level_0_infra.level_3 import create_trainer

logger = get_logger(__name__)


def train_single_fold(
    fold: int,
    n_folds: int,
    train_data: Any,
    val_data: Any,
    data_root: str,
    config: Any,
    image_size: Tuple[int, int],
    num_epochs: int,
    dataset_type: str,
    model_dir: Path,
    metric_calculator: Any = None,
) -> float:
    """
    Train a single CV fold (orchestration: coordinates trainer + dataloaders + train loop).

    Args:
        fold: Fold number (0-indexed)
        n_folds: Total number of folds
        train_data: Training data DataFrame
        val_data: Validation data DataFrame
        data_root: Data root directory
        config: Contest configuration
        image_size: Input image size
        num_epochs: Number of training epochs
        dataset_type: Dataset type
        model_dir: Base model directory
        metric_calculator: Optional metric calculator from contest context

    Returns:
        Best score for this fold
    """
    logger.info("=" * 60)
    logger.info(f"Training fold {fold+1}/{n_folds}")
    logger.info("=" * 60)

    device = get_device("auto")

    trainer = create_trainer(
        config=config,
        device=device,
        model=None,
        metric_calculator=metric_calculator,
    )

    train_loader = create_train_dataloader(
        train_data=train_data,
        data_root=data_root,
        config=config,
        image_size=image_size,
        dataset_type=dataset_type,
    )
    val_loader = create_val_dataloader(
        val_data=val_data,
        data_root=data_root,
        config=config,
        image_size=image_size,
        dataset_type=dataset_type,
    )

    fold_dir = model_dir / f"fold_{fold}"
    ensure_dir(fold_dir)

    trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        num_epochs=num_epochs,
        save_dir=fold_dir,
    )

    best_score = trainer.best_score
    logger.info(f"Fold {fold+1} best score: {best_score:.4f}")

    del trainer, train_loader, val_loader
    cleanup_gpu_memory()

    return best_score
