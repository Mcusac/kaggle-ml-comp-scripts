"""ARC stacking policy: not supported without validation OOF predictions."""

from __future__ import annotations

_STACKING_NAMES = frozenset({"stacking", "stacking_ensemble"})


def stack_explain_stacking_requirements() -> str:
    return (
        "ARC submission stacking requires out-of-fold (or validation-split) predictions "
        "for a meta-learner. The reference kernels use single/ensemble/llm_tta_dfs only; "
        "enable stacking only after you add an OOF pipeline and labeled holdout rows."
    )


def stack_raise_if_unsupported_strategy(strategy: str) -> None:
    """Raise ``ValueError`` if ``strategy`` is a stacking mode (matches prior ARC behavior)."""
    s = str(strategy or "").strip().lower()
    if s in _STACKING_NAMES:
        raise ValueError(
            f"Strategy {strategy!r} is not implemented for ARC (requires validation predictions). "
            "Use single or ensemble."
        )
