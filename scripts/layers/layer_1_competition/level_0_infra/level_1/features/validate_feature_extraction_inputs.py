"""Validate feature extraction inputs; delegates to framework guards."""

from typing import Any

from layers.layer_0_core.level_1.guards import validate_feature_extraction_trainer_inputs


def validate_feature_extraction_inputs(config: Any, device: Any) -> None:
    """Validate configuration and device for feature extraction trainer."""
    validate_feature_extraction_trainer_inputs(config, device)
