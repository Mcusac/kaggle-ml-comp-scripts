"""Feature extraction framework: cache, registry, extraction base, and embedding pipeline."""

from . import cache

from .cache import *

from .base_feature_extractor import BaseFeatureExtractor
from .feature_registry import INDIVIDUAL_FEATURES, FEATURE_PRESETS, get_feature_preset, parse_feature_spec
from .film import FiLM
from .fuse_embeddings import fuse_embeddings
from .physicochemical_features import calculate_physicochemical_properties, calculate_ctd_features
from .siglip_classes import get_siglip_image_classes, get_siglip_text_classes

__all__ = (
    # Cache
    list(cache.__all__) 
    + [
    # Extraction base
    "BaseFeatureExtractor",
    # Feature registry
    "INDIVIDUAL_FEATURES",
    "FEATURE_PRESETS",
    "get_feature_preset",
    "parse_feature_spec",
    # FiLM
    "FiLM",
    # Embedding fusion
    "fuse_embeddings",
    # Physicochemical features
    "calculate_physicochemical_properties",
    "calculate_ctd_features",
    # SigLIP class accessors
    "get_siglip_image_classes",
    "get_siglip_text_classes",
    ]
)