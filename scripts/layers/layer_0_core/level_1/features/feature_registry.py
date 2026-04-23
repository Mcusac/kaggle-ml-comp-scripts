"""
Generic registry of individual features and named feature presets.

Framework layer: contains registry mechanics only.
Concrete feature definitions must be injected by higher layers.
"""

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Registries (populated by higher layers)
# ---------------------------------------------------------------------------

INDIVIDUAL_FEATURES: Dict[str, Dict[str, Any]] = {}

FEATURE_PRESETS: Dict[str, Dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_feature_preset(preset_name: str) -> Dict[str, Any]:
    """
    Return a copy of the named feature preset configuration.
    """

    if preset_name not in FEATURE_PRESETS:
        raise ValueError(
            f"Unknown preset: {preset_name!r}. "
            f"Available presets: {list(FEATURE_PRESETS.keys())}"
        )

    preset = FEATURE_PRESETS[preset_name].copy()

    if preset.get("dimensions") is None:
        preset["dimensions"] = _calculate_dimensions(preset["features"])

    return preset


def parse_feature_spec(feature_spec: str) -> List[str]:
    """
    Parse a feature specification string into a list of feature keys.
    """

    # Preset
    if feature_spec in FEATURE_PRESETS:
        return FEATURE_PRESETS[feature_spec]["features"]

    # Comma list
    features = [f.strip() for f in feature_spec.split(",") if f.strip()]

    unknown = [f for f in features if f not in INDIVIDUAL_FEATURES]

    if unknown:
        raise ValueError(
            f"Unknown feature(s): {unknown}. "
            f"Available features: {list(INDIVIDUAL_FEATURES.keys())} "
            f"or presets: {list(FEATURE_PRESETS.keys())}"
        )

    return features


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _calculate_dimensions(features: List[str]) -> int:
    """
    Compute total feature dimensionality.
    """

    total = 0

    for feat in features:
        dims = INDIVIDUAL_FEATURES.get(feat, {}).get("dimensions")

        if dims is None:
            _logger.warning(
                "Feature %r has no known dimensions; skipping",
                feat,
            )
            continue

        total += dims

    return total