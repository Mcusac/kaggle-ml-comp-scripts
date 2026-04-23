"""timm model loading with pretrained weight fallback strategies."""

import timm

from typing import Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import (
    configure_huggingface_cache,
    resolve_offline_weight_cache,
)

_logger = get_logger(__name__)

_NETWORK_ERROR_KEYWORDS = [
    "connection", "network", "timeout", "resolve", "failed to resolve",
    "name resolution", "temporary failure", "max retries",
    "metadataincompletebuffer", "incomplete", "corrupt", "deserializing",
]


def _create_timm_model(model_name: str, num_classes: int, pretrained: bool) -> object:
    """Create a timm model with the given settings."""
    return timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)


def _is_network_error(error: Exception) -> bool:
    """Return True if error is network- or download-related."""
    return any(keyword in str(error).lower() for keyword in _NETWORK_ERROR_KEYWORDS)


class TimmWeightLoader:
    """
    Load pretrained weights for timm models with offline/Kaggle fallback.

    Attempts to load pretrained weights directly, then falls back to a
    reconfigured HuggingFace cache (Kaggle offline datasets), and finally
    to a non-pretrained model if both strategies fail.
    """

    def __init__(self) -> None:
        self._pretrained_loaded = False

    def is_pretrained_loaded(self) -> bool:
        """Return True if pretrained weights were successfully loaded."""
        return self._pretrained_loaded

    def _try_pretrained(self, model_name: str, num_classes: int) -> Optional[object]:
        """
        Attempt to load pretrained weights directly.

        Returns the model on success. On network errors, delegates to
        _try_offline_cache. On other errors, logs an error and returns None.
        """
        try:
            backbone = _create_timm_model(model_name, num_classes, pretrained=True)
            self._pretrained_loaded = True
            _logger.info("Loaded pretrained weights for %s", model_name)
            return backbone

        except Exception as e:
            if _is_network_error(e):
                return self._try_offline_cache(model_name, num_classes, e)

            _logger.error(
                "Unexpected failure loading pretrained weights for %s: %s",
                model_name,
                e,
            )
            return None

    def _try_offline_cache(
        self,
        model_name: str,
        num_classes: int,
        original_error: Exception,
    ) -> Optional[object]:
        """
        Reconfigure HuggingFace cache to an offline directory and retry.

        Returns the model on success, None if no offline weights are found
        or loading fails again.
        """
        _logger.warning("Network/download error loading pretrained weights: %s", original_error)

        cache_path, _ = resolve_offline_weight_cache()
        if cache_path is None:
            _logger.warning("No offline weight cache found")
            return None

        _logger.info("Retrying with offline cache: %s", cache_path)
        configure_huggingface_cache(cache_path)

        try:
            backbone = _create_timm_model(model_name, num_classes, pretrained=True)
            self._pretrained_loaded = True
            _logger.info("Loaded pretrained weights from offline cache for %s", model_name)
            return backbone
        except Exception as e:
            _logger.warning("Offline cache retry failed: %s", e)
            return None

    def load_weights(self, model_name: str, num_classes: int, pretrained: bool = True) -> object:
        """
        Load a timm model with pretrained weight fallback chain if requested.

        Strategy when pretrained=True:
          1. Direct download / local HuggingFace cache
          2. Reconfigure to offline Kaggle weight directory and retry
          3. Fall back to non-pretrained model

        Args:
            model_name:  timm model identifier.
            num_classes: Output class count (0 for feature extraction).
            pretrained:  Whether to attempt loading pretrained weights.

        Returns:
            timm model instance.
        """
        if not pretrained:
            self._pretrained_loaded = False
            _logger.info("Created non-pretrained model: %s", model_name)
            return _create_timm_model(model_name, num_classes, pretrained=False)

        cache_path, has_internet = resolve_offline_weight_cache()
        if cache_path:
            _logger.info("Offline weight cache available: %s", cache_path)
        elif not has_internet:
            _logger.warning(
                "No internet and no offline weights — will fall back to "
                "non-pretrained if download fails"
            )

        backbone = self._try_pretrained(model_name, num_classes)
        if backbone is not None:
            return backbone

        _logger.warning("Falling back to non-pretrained model for %s", model_name)
        self._pretrained_loaded = False
        return _create_timm_model(model_name, num_classes, pretrained=False)