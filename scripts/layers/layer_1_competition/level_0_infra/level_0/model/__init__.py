"""Auto-generated package exports."""


from .embeddings import (
    load_embedding_data,
    load_structured_features,
)

from .feature_catalog import register_features

from .model_constants import (
    MODEL_ID_MAP,
    get_model_image_size,
    get_model_name_from_pretrained,
    get_pretrained_weights_path,
    register_model_id_map,
)

__all__ = [
    "MODEL_ID_MAP",
    "get_model_image_size",
    "get_model_name_from_pretrained",
    "get_pretrained_weights_path",
    "load_embedding_data",
    "load_structured_features",
    "register_features",
    "register_model_id_map",
]
