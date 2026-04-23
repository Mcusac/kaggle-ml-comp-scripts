"""Grid search variant execution logging."""

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def log_variant_header(
    variant_index: int,
    total_variants: int,
    variant_info: str,
) -> None:
    """
    Log a separator header marking the start of a grid search variant run.

    Args:
        variant_index: Zero-based index of the variant.
        total_variants: Total number of variants in this search.
        variant_info: Human-readable description of the variant being run.
    """
    _logger.info("=" * 60)
    _logger.info("Variant %d/%d", variant_index + 1, total_variants)
    _logger.info("%s", variant_info)
    _logger.info("=" * 60)