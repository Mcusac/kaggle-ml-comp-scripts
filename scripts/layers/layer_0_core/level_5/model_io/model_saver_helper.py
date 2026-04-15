"""Model saver helper for feature extraction trainer. Uses level_0 and level_4 save_pickle/save_json."""

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import ensure_dir
from layers.layer_0_core.level_4 import save_json, save_pickle


def save_regression_model(model: Any, save_dir: Path) -> None:
    """
    Save trained regression model and metadata.
    
    Args:
        model: Trained regression model.
        save_dir: Directory to save model to.
    """
    ensure_dir(save_dir)
    model_path = save_dir / 'regression_model.pkl'
    save_pickle(model, model_path)
    
    # Save metadata
    metadata = {
        'model_type': type(model).__name__,
        'model_path': str(model_path)
    }
    metadata_path = save_dir / 'metadata.json'
    save_json(metadata, metadata_path)
