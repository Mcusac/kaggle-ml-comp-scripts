"""Strategy dispatch skeleton helpers (model count validation only)."""

from typing import Sequence


def validate_strategy_models(strategy: str, models: Sequence[str]) -> None:
    """
    Validate common submission strategies against model list length.

    This does not enforce contest-specific strategy semantics; it only validates
    the common `single`/`ensemble`/`stacking` expectations.
    """
    s = str(strategy or "").strip().lower()
    n = len(list(models))
    if s == "single":
        if n != 1:
            raise ValueError(f"Strategy 'single' requires exactly 1 model, got {n}")
        return
    if s in ("ensemble", "stacking", "stacking_ensemble"):
        if n < 2:
            raise ValueError(f"Strategy {s!r} requires at least 2 models, got {n}")
        return
    raise ValueError(f"Unknown strategy: {strategy}")


__all__ = ["validate_strategy_models"]

