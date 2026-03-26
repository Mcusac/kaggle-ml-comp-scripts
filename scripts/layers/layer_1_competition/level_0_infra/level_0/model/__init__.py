"""Model metadata, feature-extraction config helpers, and export verification."""

from .detect_model_type import detect_model_type
from .embeddings import load_embedding_data, load_structured_features
from .feature_catalog import register_features
from .feature_extraction import (
    get_dataset_type,
    get_feature_extraction_mode,
    get_feature_extraction_model_name,
    get_regression_model_type,
)
from .model_constants import (
    MODEL_ID_MAP,
    get_model_id,
    get_model_image_size,
    get_model_name_from_pretrained,
    get_pretrained_weights_path,
)
from .verify_export_output import verify_export_output

__all__ = [
    "MODEL_ID_MAP",
    "detect_model_type",
    "get_dataset_type",
    "get_feature_extraction_mode",
    "get_feature_extraction_model_name",
    "get_model_id",
    "get_model_image_size",
    "get_model_name_from_pretrained",
    "get_pretrained_weights_path",
    "get_regression_model_type",
    "load_embedding_data",
    "load_structured_features",
    "register_features",
    "verify_export_output",
]
