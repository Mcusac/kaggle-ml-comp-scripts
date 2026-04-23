"""
Training component setup utilities.
"""

from typing import Any, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger, get_torch, get_config_value

_logger = get_logger(__name__)


def setup_mixed_precision(
    config: Any,
    device: Any,
) -> Tuple[bool, Optional[Any]]:
    """
    Set up mixed precision training (GradScaler).

    Returns:
        use_mixed_precision: bool
        scaler: torch.amp.GradScaler or None
    """
    torch = get_torch()

    use_mixed_precision = get_config_value(
        config,
        "training.use_mixed_precision",
        default=False,
    )

    scaler = None

    if use_mixed_precision and device.type == "cuda":
        try:
            scaler = torch.amp.GradScaler()
            _logger.info("Mixed precision (FP16) training enabled")
        except Exception:
            _logger.warning(
                "Mixed precision requested but not available"
            )
            use_mixed_precision = False

    return use_mixed_precision, scaler