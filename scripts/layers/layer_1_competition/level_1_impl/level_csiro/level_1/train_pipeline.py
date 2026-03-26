"""Train-only pipeline for CSIRO contest.

Moved from orchestration to contest layer; orchestration must not depend on contest.
Callers that need this pipeline should import from contest.implementations.csiro.train_pipeline.
"""

from pathlib import Path
from typing import Optional, Tuple, List

from layers.layer_0_core.level_0 import get_logger, ensure_dir
from layers.layer_0_core.level_1 import create_kfold_splits, get_fold_data
from layers.layer_1_competition.level_0_infra.level_4 import train_single_fold

from layers.layer_1_competition.level_0_infra.level_0 import create_training_config, get_model_image_size
from layers.layer_1_competition.level_0_infra.level_1 import get_contest

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import calc_metric, aggregate_train_csv

logger = get_logger(__name__)


def train_pipeline(
    data_root: Optional[str] = None,
    model: Optional[str] = None,
    batch_size: int = 32,
    num_epochs: int = 100,
    learning_rate: float = 1e-3,
    optimizer: str = 'AdamW',
    loss_function: str = 'SmoothL1Loss',
    scheduler: str = 'ReduceLROnPlateau',
    dataset_type: str = 'split',
    n_folds: int = 5,
    **kwargs
) -> Tuple[float, List[float]]:
    """
    Run training-only pipeline with cross-validation for CSIRO contest.

    Args:
        data_root: Data root directory (default: from contest paths).
        model: Model name (e.g., 'dinov2_base', 'efficientnet_b0').
        batch_size: Batch size for training.
        num_epochs: Number of training epochs.
        learning_rate: Learning rate.
        optimizer: Optimizer type ('AdamW', 'Adam', 'SGD').
        loss_function: Loss function ('SmoothL1Loss', 'MSELoss', 'L1Loss').
        scheduler: Scheduler type ('ReduceLROnPlateau', 'CosineAnnealingLR').
        dataset_type: Dataset type ('full' or 'split').
        n_folds: Number of cross-validation folds.
        **kwargs: Additional arguments (model_name, etc.).

    Returns:
        Tuple of (avg_cv_score, fold_scores).
    """
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()

    if data_root is None:
        data_root = str(paths.get_data_root())

    if model is None:
        model = kwargs.get('model_name', 'dinov2_base')

    create_training_config(
        batch_size, num_epochs, learning_rate, optimizer,
        loss_function, scheduler, config
    )

    image_size = get_model_image_size(model)

    train_csv_path = Path(data_root) / 'train.csv'
    if not train_csv_path.exists():
        raise FileNotFoundError(f"Train CSV not found: {train_csv_path}")

    logger.info(f"Loading train data from {train_csv_path}")
    agg_train_df = aggregate_train_csv(train_csv_path)
    agg_train_df = create_kfold_splits(
        agg_train_df,
        n_folds=n_folds,
        shuffle=True,
        random_state=42
    )

    all_scores = []
    model_dir = Path(paths.get_models_base_dir())
    ensure_dir(model_dir)

    for fold in range(n_folds):
        train_data = get_fold_data(agg_train_df, fold, train=True)
        val_data = get_fold_data(agg_train_df, fold, train=False)

        best_score = train_single_fold(
            fold, n_folds, train_data, val_data, data_root,
            config, image_size, num_epochs, dataset_type, model_dir,
            metric_calculator=calc_metric,
        )
        all_scores.append(best_score)

    avg_cv_score = sum(all_scores) / len(all_scores) if all_scores else -float('inf')

    logger.info("=" * 60)
    logger.info("Cross-validation summary:")
    logger.info(f"Average CV score: {avg_cv_score:.4f}")
    logger.info(f"Individual fold scores: {all_scores}")
    logger.info("=" * 60)

    return avg_cv_score, all_scores
