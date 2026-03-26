"""Validate feature extraction inputs. Delegates to infra level_1."""

from typing import Any


def validate_feature_extraction_inputs(
    config: Any,
    device: Any,
) -> None:
    """Validate configuration and device for feature extraction trainer."""

    from layers.layer_1_competition.level_0_infra.level_1.features import (
        validate_feature_extraction_inputs as _validate,
    )

    _validate(config, device)
