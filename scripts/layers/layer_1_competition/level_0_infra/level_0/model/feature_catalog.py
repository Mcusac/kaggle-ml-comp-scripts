"""
Contest-specific feature definitions.

Registers biological embedding and handcrafted features.
"""

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import INDIVIDUAL_FEATURES, FEATURE_PRESETS

logger = get_logger(__name__)


def register_features() -> None:
    """
    Populate global feature registries.
    """

    # ------------------------------------------------------------------
    # Individual features
    # ------------------------------------------------------------------

    INDIVIDUAL_FEATURES.update(
        {
            "protbert": {
                "name": "ProtBERT",
                "dimensions": 1024,
                "type": "embedding",
                "description": "ProtBERT protein embeddings",
            },
            "esm2": {
                "name": "ESM2",
                "dimensions": 1280,
                "type": "embedding",
                "description": "ESM2 evolutionary embeddings",
            },
            "t5": {
                "name": "T5",
                "dimensions": 1024,
                "type": "embedding",
                "description": "T5 protein embeddings",
            },
            "hc": {
                "name": "Handcrafted",
                "dimensions": 90,
                "type": "engineered",
                "description": "90 handcrafted features",
            },
        }
    )

    # ------------------------------------------------------------------
    # Presets
    # ------------------------------------------------------------------

    FEATURE_PRESETS.update(
        {
            "default": {
                "features": ["protbert", "esm2", "hc"],
                "description": "ProtBERT + ESM2 + handcrafted (2394 dims)",
                "dimensions": 2394,
            },
            "high_quality": {
                "features": ["protbert", "esm2", "t5", "hc"],
                "description": "ProtBERT + ESM2 + T5 + handcrafted (3418 dims)",
                "dimensions": 3418,
            },
            "embeddings_only": {
                "features": ["protbert", "esm2"],
                "description": "ProtBERT + ESM2 embeddings only (2304 dims)",
                "dimensions": 2304,
            },
            "protbert_only": {
                "features": ["protbert"],
                "description": "ProtBERT only (1024 dims)",
                "dimensions": 1024,
            },
            "handcrafted_only": {
                "features": ["hc"],
                "description": "Handcrafted features only (90 dims)",
                "dimensions": 90,
            },
        }
    )

    logger.info(
        "Registered %d features and %d presets",
        len(INDIVIDUAL_FEATURES),
        len(FEATURE_PRESETS),
    )
