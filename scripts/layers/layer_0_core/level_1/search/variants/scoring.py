"""Grid search best score tracking."""

from typing import Any, Dict, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def select_best_score(
    current_best_score: float,
    new_score: Optional[float],
    new_result: Dict[str, Any],
) -> Tuple[float, Optional[Dict[str, Any]]]:
    """
    Return the better score and its result dict.

    If new_score is greater than current_best_score, returns new_score
    and new_result. Otherwise returns current_best_score and None,
    signalling no improvement.

    Args:
        current_best_score: The best score recorded so far.
        new_score: The score from the latest variant. None if the variant failed.
        new_result: The result dict from the latest variant.

    Returns:
        Tuple of (best_score, best_result_or_None).
    """
    if new_score is not None and new_score > current_best_score:
        _logger.info("New best score: %.4f", new_score)
        return new_score, new_result

    return current_best_score, None