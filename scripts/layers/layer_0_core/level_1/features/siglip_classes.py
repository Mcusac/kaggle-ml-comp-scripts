"""Lazy accessors for SigLIP-related transformer classes.

Imports are deferred to call time so that the transformers library
remains an optional dependency — callers that never invoke these
functions pay no import cost and see no import errors.
"""

from typing import Any, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def get_siglip_image_classes() -> Tuple[Optional[Any], Optional[Any]]:
    """Return (AutoModel, AutoImageProcessor) from the transformers library.

    Returns:
        Tuple of (AutoModel, AutoImageProcessor), or (None, None) if the
        transformers library is not installed.
    """
    try:
        from transformers import AutoModel, AutoImageProcessor
        return AutoModel, AutoImageProcessor
    except ImportError:
        logger.warning("transformers not available. SigLIP image extraction disabled.")
        return None, None


def get_siglip_text_classes() -> Tuple[Optional[Any], Optional[Any]]:
    """Return (AutoModel, AutoTokenizer) from the transformers library.

    Returns:
        Tuple of (AutoModel, AutoTokenizer), or (None, None) if the
        transformers library is not installed.
    """
    try:
        from transformers import AutoModel, AutoTokenizer
        return AutoModel, AutoTokenizer
    except ImportError:
        logger.warning("transformers not available. SigLIP text extraction disabled.")
        return None, None