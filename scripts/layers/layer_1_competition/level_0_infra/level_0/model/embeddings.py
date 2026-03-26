"""Placeholder hooks for contest-specific embedding and structured feature loading."""

import numpy as np

from pathlib import Path
from typing import List, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def load_embedding_data(
    embedding_type: str,
    datatype: str = "train",
    use_memmap: Optional[bool] = None,
    base_path: Optional[Path] = None,
) -> Tuple[np.ndarray, List[str]]:
    """Placeholder for loading embeddings. Contest layer must provide a real implementation."""
    raise NotImplementedError(
        "load_embedding_data() is a framework-level placeholder. "
        f"Requested: embedding_type={embedding_type!r}, datatype={datatype!r}"
    )


def load_structured_features(
    feature_type: str,
    datatype: str = "train",
    use_memmap: Optional[bool] = None,
    base_path: Optional[Path] = None,
) -> Tuple[np.ndarray, List[str]]:
    """Placeholder for loading structured features. Contest layer must provide a real implementation."""
    raise NotImplementedError(
        "load_structured_features() is a framework-level placeholder. "
        f"Requested: feature_type={feature_type!r}, datatype={datatype!r}"
    )
