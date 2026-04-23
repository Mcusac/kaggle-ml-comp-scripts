"""Auto-generated mixed exports."""


from . import cache

from .cache import *

from .base_feature_extractor import BaseFeatureExtractor

from .feature_registry import (
    FEATURE_PRESETS,
    INDIVIDUAL_FEATURES,
    get_feature_preset,
    parse_feature_spec,
)

from .film import FiLM

from .fuse_embeddings import fuse_embeddings

from .physicochemical_features import (
    calculate_ctd_features,
    calculate_physicochemical_properties,
)

from .siglip_classes import (
    get_siglip_image_classes,
    get_siglip_text_classes,
)

__all__ = (
    list(cache.__all__)
    + [
        "BaseFeatureExtractor",
        "FEATURE_PRESETS",
        "FiLM",
        "INDIVIDUAL_FEATURES",
        "calculate_ctd_features",
        "calculate_physicochemical_properties",
        "fuse_embeddings",
        "get_feature_preset",
        "get_siglip_image_classes",
        "get_siglip_text_classes",
        "parse_feature_spec",
    ]
)
