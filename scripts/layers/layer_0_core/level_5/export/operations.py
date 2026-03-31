"""Atomic export operations and scenario-specific export functions"""

import shutil

from pathlib import Path
from typing import Dict, Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_4 import save_json, load_json

logger = get_logger(__name__)


def find_trained_model_path(
    model_dir: Path,
    best_fold: int = None
) -> tuple[Path, int]:
    """
    Find model checkpoint path from training directory.

    Supports PyTorch checkpoints (best_model.pth) and regression models (regression_model.pkl).
    When best_fold is None, selects the best fold by score from checkpoint metadata.

    Args:
        model_dir: Base model directory (e.g., models/best_model_training/).
        best_fold: Optional fold number. If None, finds best fold from metadata.

    Returns:
        Tuple of (model_path, fold_number).

    Raises:
        FileNotFoundError: If no model checkpoint found.
    """
    model_dir = Path(model_dir)
    
    if best_fold is not None:
        return _find_model_for_specific_fold(model_dir, best_fold)
    else:
        return _find_best_fold_model(model_dir)


def _find_model_for_specific_fold(model_dir: Path, fold: int) -> tuple[Path, int]:
    """Find model checkpoint for a specific fold."""
    fold_dir = model_dir / f'fold_{fold}'
    
    # Try regular checkpoint first
    checkpoint_path = fold_dir / 'best_model.pth'
    if checkpoint_path.exists():
        return checkpoint_path, fold
    
    # Try regression model
    regression_path = fold_dir / 'regression_model.pkl'
    if regression_path.exists():
        return regression_path, fold
    
    raise FileNotFoundError(f"Model checkpoint not found for fold {fold}: {fold_dir}")


def _find_best_fold_model(model_dir: Path) -> tuple[Path, int]:
    """Find best fold model by checking all folds."""
    best_fold_num = None
    best_score = -float('inf')
    best_path = None
    
    # Check up to 10 folds
    for fold in range(10):
        fold_dir = model_dir / f'fold_{fold}'
        if not fold_dir.exists():
            continue
        
        # Check regular checkpoint
        path, score = _check_regular_checkpoint(fold_dir)
        if path and score > best_score:
            best_score = score
            best_fold_num = fold
            best_path = path
            continue
        
        # Check regression model
        path, score = _check_regression_model(fold_dir)
        if path and score > best_score:
            best_score = score
            best_fold_num = fold
            best_path = path
    
    if best_fold_num is None:
        raise FileNotFoundError(f"No valid checkpoints found in {model_dir}")
    
    return best_path, best_fold_num


def _check_regular_checkpoint(fold_dir: Path) -> tuple[Optional[Path], float]:
    """Check for regular PyTorch checkpoint and extract score."""
    checkpoint_path = fold_dir / 'best_model.pth'
    if not checkpoint_path.exists():
        return None, -float('inf')
    
    score = _extract_score_from_checkpoint_metadata(fold_dir)
    return checkpoint_path, score


def _check_regression_model(fold_dir: Path) -> tuple[Optional[Path], float]:
    """Check for regression model and extract score."""
    regression_path = fold_dir / 'regression_model.pkl'
    regression_info_path = fold_dir / 'regression_model_info.json'
    
    if not (regression_path.exists() and regression_info_path.exists()):
        return None, -float('inf')
    
    score = _extract_score_from_regression_info(regression_info_path)
    return regression_path, score


def _extract_score_from_json(path: Path, default: float = -float('inf')) -> float:
    """Extract best_score from a JSON file (checkpoint metadata or regression info)."""
    if not path.exists():
        return default
    try:
        data = load_json(path)
        return data.get('best_score', default)
    except Exception:
        return default


def _extract_score_from_checkpoint_metadata(fold_dir: Path) -> float:
    """Extract score from checkpoint metadata file."""
    return _extract_score_from_json(fold_dir / 'checkpoint_metadata.json')


def _extract_score_from_regression_info(info_path: Path) -> float:
    """Extract score from regression model info file."""
    return _extract_score_from_json(info_path)


def export_from_training_dir(
    model_dir: Path,
    export_dir: Path,
    metadata: Dict[str, Any]
) -> None:
    """
    Export model from just-trained model directory.
    
    This function handles the export of models from a training directory
    structure (fold_0/, fold_1/, etc.) to a flat export structure.
    Supports both regular PyTorch checkpoints and feature extraction regression models.
    
    Args:
        model_dir: Base model directory containing fold checkpoints
        export_dir: Destination directory for export
        metadata: Complete metadata dictionary
        
    Raises:
        FileNotFoundError: If model checkpoint not found
        RuntimeError: If export fails
    """
    # Find model checkpoint
    model_path, best_fold_used = find_trained_model_path(model_dir, metadata.get('best_fold'))
    
    # Ensure metadata has correct best_fold
    metadata['best_fold'] = best_fold_used
    
    # Determine export filename based on model type
    if model_path.suffix == '.pkl':
        # Feature extraction regression model
        export_filename = 'regression_model.pkl'
    else:
        # Regular PyTorch checkpoint
        export_filename = 'best_model.pth'
    
    # Perform atomic export operations
    copy_model_checkpoint(model_path, export_dir / export_filename)
    write_metadata_file(metadata, export_dir / 'model_metadata.json')
    
    logger.info("✅ Model exported from training directory")
    logger.info(f"   Model: {export_dir / export_filename}")
    logger.info(f"   Metadata: {export_dir / 'model_metadata.json'}")


def copy_model_checkpoint(source: Path, dest: Path) -> None:
    """
    Atomic operation: Copy model checkpoint file.
    
    Args:
        source: Path to source checkpoint file
        dest: Path to destination checkpoint file (must include filename)
        
    Raises:
        FileNotFoundError: If source doesn't exist
        OSError: If copy fails
    """
    if not source.exists():
        raise FileNotFoundError(f"Source checkpoint not found: {source}")
    
    # Ensure destination directory exists
    ensure_dir(dest.parent)
    
    # Copy file
    shutil.copy2(source, dest)
    logger.debug(f"Copied checkpoint: {source} -> {dest}")


def write_metadata_file(metadata: Dict[str, Any], dest: Path) -> None:
    """
    Atomic operation: Write metadata dictionary to JSON file.
    
    Args:
        metadata: Metadata dictionary to write
        dest: Path to destination JSON file (must include filename)
        
    Raises:
        OSError: If write fails
    """
    # Ensure destination directory exists
    ensure_dir(dest.parent)
    
    # Write JSON file
    save_json(metadata, dest)
    logger.debug(f"Wrote metadata: {dest}")
