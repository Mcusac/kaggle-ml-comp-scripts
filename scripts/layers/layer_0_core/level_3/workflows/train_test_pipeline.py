"""Train-test pipeline. Requires contest_context and train_pipeline_fn from contest (orchestration does not import contest)."""

from typing import Optional, Any

from layers.layer_0_core.level_0 import get_fold_checkpoint_path, get_logger
from layers.layer_0_core.level_2 import find_best_fold_from_scores

logger = get_logger(__name__)


def train_test_pipeline(
    contest_context: Any,
    train_pipeline_fn: Optional[Any] = None,
    data_root: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> None:
    """
    Train model with cross-validation and then test with best fold.
    Contest passes contest_context and train_pipeline_fn.
    """
    if train_pipeline_fn is None:
        raise ValueError("train_pipeline_fn is required. Contest must pass its train_pipeline.")
    paths = contest_context.get_paths()

    # Resolve data root
    if data_root is None:
        data_root = str(paths.get_data_root())

    # Train
    logger.info("=" * 60)
    logger.info("Starting training phase...")
    logger.info("=" * 60)
    avg_cv_score, fold_scores = train_pipeline_fn(
        data_root=data_root,
        model=model,
        **kwargs
    )
    
    # Find best fold
    if not fold_scores:
        raise RuntimeError("No fold scores available. Training may have failed.")
    
    best_fold, best_score = find_best_fold_from_scores(fold_scores)
    logger.info(f"\n✅ Best fold: {best_fold} with score: {best_score:.4f}")
    
    # Get model directory
    model_dir = paths.get_models_base_dir()
    model_path = get_fold_checkpoint_path(model_dir, best_fold)
    
    if not model_path.exists():
        raise FileNotFoundError(
            f"Best fold checkpoint not found: {model_path}. "
            f"Training may have failed for fold {best_fold}."
        )
    
    # Test (use best fold model; test_pipeline from contest context)
    logger.info("\n" + "=" * 60)
    logger.info("Starting testing phase...")
    logger.info("=" * 60)
    test_pipeline_fn = contest_context.get_test_pipeline()
    test_pipeline_fn(
        contest_context=contest_context,
        data_root=data_root,
        model_path=str(model_path),
        **kwargs
    )
    
    logger.info("=" * 60)
    logger.info("✅ Train-test pipeline complete")
    logger.info("=" * 60)
