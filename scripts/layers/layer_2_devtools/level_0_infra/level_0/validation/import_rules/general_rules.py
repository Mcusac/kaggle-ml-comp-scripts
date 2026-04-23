"""General-stack import rule helpers for devtools scanners.

Single source of truth for `from level_N import` classification (tuples, stable kinds).
Re-exported from ``level_0_infra.level_1.general_rules`` for backward compatibility.
"""

from __future__ import annotations

from ...constants.import_patterns import DEEP_LEVEL_RE, LEVEL_DIR_RE


def has_deep_level_path(module_name: str) -> bool:
    """True when import target is a deep path ``level_N.<submod>...`` (not a barrel)."""
    return DEEP_LEVEL_RE.match(module_name) is not None


def classify_general_import_from(
    module_name: str, current_level: int
) -> tuple[str, int] | None:
    """
    Classify ``from <module_name> import ...`` for general-stack *logic* files.

    Returns:
        ``("WRONG_LEVEL", imported)`` for same-level barrel imports in logic,
        ``("UPWARD", imported)`` for imports from a higher level than the file,
        or ``None`` for allowed lower-level / non-``level_N`` top-level forms.
    """
    match = LEVEL_DIR_RE.fullmatch(module_name)
    if not match:
        return None
    imported_level = int(match.group(1))
    if imported_level == current_level:
        return ("WRONG_LEVEL", imported_level)
    if imported_level > current_level:
        return ("UPWARD", imported_level)
    return None
