"""Convenience wrapper for SigLIP extraction."""

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Optional, Union

from layers.layer_0_core.level_3 import SigLIPExtractor


def compute_siglip_embeddings(
    model_path: str,
    df: pd.DataFrame,
    image_path_col: str = "image_path",
    image_root: Optional[Union[str, Path]] = None,
    **kwargs,
) -> np.ndarray:
    """
    Extract SigLIP embeddings for all images in a DataFrame.

    Args:
        model_path: Path to SigLIP model weights.
        df: DataFrame with image paths.
        image_path_col: Column name for image paths (default: "image_path").
        image_root: Optional root path to prepend to relative paths.
        **kwargs: Additional arguments passed to SigLIPExtractor.

    Returns:
        Embeddings array of shape (n_samples, embedding_dim).
    """
    extractor = SigLIPExtractor(model_path=model_path, **kwargs)

    if image_root:
        image_paths = [
            str(Path(image_root) / Path(p))
            for p in df[image_path_col]
        ]
    else:
        image_paths = df[image_path_col].tolist()

    return extractor.extract_batch(image_paths)
