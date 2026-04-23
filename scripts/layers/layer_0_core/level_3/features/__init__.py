"""Auto-generated package exports."""


from .extract_all_features import extract_all_features

from .handcrafted_feature_extraction import (
    extract_handcrafted_features_for_ids,
    extract_handcrafted_parallel,
    stream_features,
)

from .siglip_extractor import (
    ModelResolver,
    SigLIPExtractor,
)

from .supervised_embedding_engine import SupervisedEmbeddingEngine

__all__ = [
    "ModelResolver",
    "SigLIPExtractor",
    "SupervisedEmbeddingEngine",
    "extract_all_features",
    "extract_handcrafted_features_for_ids",
    "extract_handcrafted_parallel",
    "stream_features",
]
