"""Feature extraction model creation and validation."""

from .feature_extractor_factory import create_feature_extraction_model, set_pretrained_weights_resolver

__all__ = (
    "create_feature_extraction_model",
    "set_pretrained_weights_resolver",
)
