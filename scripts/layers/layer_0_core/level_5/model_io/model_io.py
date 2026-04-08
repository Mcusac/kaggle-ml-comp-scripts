"""Model I/O utilities."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from level_0 import (
    ModelError,
    ModelLoadError,
    ensure_dir,
    get_logger,
    get_torch,
    is_torch_available,
)
from level_3 import validate_file_exists
from level_4 import load_json, load_pickle, save_json, save_pickle

logger = get_logger(__name__)
torch = get_torch()
TORCH_AVAILABLE = is_torch_available()


def save_model_raw(
    model: Any,
    path: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Save model without validation or logging.

    Args:
        model: Model object to save.
        path: Destination file path.
        metadata: Optional metadata dict (hyperparams, metrics, etc.).

    Returns:
        Path to saved model.

    Raises:
        ModelError: If save fails or model type cannot be determined.
    """
    path = Path(path)
    ensure_dir(path.parent)

    if metadata is not None:
        metadata = dict(metadata)
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.now().isoformat()

    try:
        if TORCH_AVAILABLE and hasattr(model, 'state_dict'):
            _save_pytorch_model(model, path, metadata)
        else:
            _save_pickle_backed_model(model, path, metadata)
    except Exception as e:
        raise ModelError(f"Failed to save model to {path}: {e}")

    if metadata is not None:
        try:
            _save_metadata(path, metadata)
        except Exception as e:
            logger.warning(f"Failed to save metadata for {path}: {e}")

    return path


def save_model(
    model: Any,
    path: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Save model with validation and logging.

    Supports PyTorch (.pth/.pt), scikit-learn (.pkl), and generic pickle (.pkl).
    Metadata is stored in a separate .metadata.json sidecar file.

    Args:
        model: Model object to save.
        path: Destination file path.
        metadata: Optional metadata dict. Timestamp added automatically.

    Returns:
        Path to saved model.

    Raises:
        ModelError: If model is None or save fails.
    """
    if model is None:
        raise ModelError("Model cannot be None")

    path = Path(path)

    try:
        result_path = save_model_raw(model, path, metadata)
        model_type = _get_model_type_name(model)
        size_mb = path.stat().st_size / (1024 * 1024)
        logger.info(f"Saved {model_type} model: {path} ({size_mb:.2f}MB)")
        return result_path
    except ModelError:
        raise
    except Exception as e:
        raise ModelError(f"Failed to save model to {path}: {e}")


def load_model_raw(
    path: Union[str, Path],
) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Load model without validation or logging.

    Args:
        path: Path to model file.

    Returns:
        (model, metadata) tuple. metadata is None if no sidecar file exists.

    Raises:
        FileNotFoundError: If model file doesn't exist.
        ModelLoadError: If model cannot be loaded.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")

    try:
        if path.suffix in {'.pth', '.pt'}:
            model, metadata = _load_pytorch_model(path)
        elif path.suffix == '.pkl':
            model, metadata = _load_pickle_model(path)
        else:
            raise ModelLoadError(
                f"Unsupported model format: {path.suffix}. Supported: .pth, .pt, .pkl"
            )
    except (FileNotFoundError, ModelLoadError):
        raise
    except Exception as e:
        raise ModelLoadError(f"Failed to load model from {path}: {e}")

    if metadata is None:
        try:
            metadata = _load_metadata(path)
        except Exception as e:
            logger.debug(f"No metadata sidecar found for {path}: {e}")

    return model, metadata


def load_model(
    path: Union[str, Path],
) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """
    Load model with validation and logging.

    Detects format from file extension (.pth/.pt for PyTorch, .pkl for pickle).

    Args:
        path: Path to model file.

    Returns:
        (model, metadata) tuple.

    Raises:
        FileNotFoundError: If model file doesn't exist.
        ModelLoadError: If model cannot be loaded or format is unsupported.
    """
    try:
        path_obj = validate_file_exists(path, name="Model file")
    except FileNotFoundError:
        raise
    except Exception as e:
        raise ModelLoadError(f"Invalid model path: {e}")

    try:
        model, metadata = load_model_raw(path_obj)
        logger.info(f"Loaded model: {path_obj}")
        if metadata:
            logger.debug(f"Model metadata keys: {list(metadata.keys())}")
        return model, metadata
    except (FileNotFoundError, ModelLoadError):
        raise
    except Exception as e:
        raise ModelLoadError(f"Failed to load model from {path}: {e}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _save_pytorch_model(
    model: Any,
    path: Path,
    metadata: Optional[Dict[str, Any]],
) -> None:
    """Save PyTorch model as a checkpoint dict."""
    if not TORCH_AVAILABLE:
        raise ModelError("PyTorch not installed")
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'model_class': model.__class__.__name__,
        'model_module': model.__class__.__module__,
    }
    if metadata:
        checkpoint['metadata'] = metadata
    torch.save(checkpoint, path)


def _save_pickle_backed_model(
    model: Any,
    path: Path,
    metadata: Optional[Dict[str, Any]],
) -> None:
    """Save sklearn or other pickle-compatible model via level_4 save_pickle."""
    data = {
        'model': model,
        'model_class': model.__class__.__name__,
        'model_module': model.__class__.__module__,
    }
    if metadata:
        data['metadata'] = metadata
    save_pickle(data, path)


def _load_pytorch_model(
    path: Path,
) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """Load PyTorch checkpoint dict."""
    if not TORCH_AVAILABLE:
        raise ModelLoadError("PyTorch not installed")
    try:
        checkpoint = torch.load(path, map_location='cpu')
    except Exception as e:
        raise ModelLoadError(f"Failed to load PyTorch checkpoint: {e}")
    return checkpoint, checkpoint.get('metadata')


def _load_pickle_model(
    path: Path,
) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """Load pickle model via level_4 load_pickle."""
    data = load_pickle(path)
    if isinstance(data, dict) and 'model' in data:
        return data['model'], data.get('metadata')
    return data, None


def _save_metadata(path: Path, metadata: Dict[str, Any]) -> None:
    """Persist serialisable metadata keys as a sidecar JSON file."""
    safe = {
        k: v for k, v in metadata.items()
        if isinstance(v, (str, int, float, bool, type(None), list, dict))
    }
    save_json(safe, path.with_suffix(path.suffix + '.metadata.json'))


def _load_metadata(path: Path) -> Optional[Dict[str, Any]]:
    """Load sidecar metadata JSON if it exists."""
    metadata_path = path.with_suffix(path.suffix + '.metadata.json')
    if not metadata_path.exists():
        return None
    try:
        return load_json(metadata_path)
    except Exception:
        return None


def _get_model_type_name(model: Any) -> str:
    """Return a human-readable model type label."""
    if TORCH_AVAILABLE and hasattr(model, 'state_dict'):
        return "PyTorch"
    if hasattr(model, '__sklearn_is_fitted__') or hasattr(model, 'fit'):
        return "scikit-learn"
    return "pickle-backed"