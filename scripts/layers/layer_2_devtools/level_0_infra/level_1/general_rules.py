"""Atomic import-rule classifiers used by devtools scanners."""

from layers.layer_2_devtools.level_0_infra.level_0 import (
    DEEP_LEVEL_RE,
    LEVEL_DIR_RE,
)


def has_deep_level_path(module_name: str) -> bool:
    """Return True when module path starts with level_N.<subpath>."""
    return DEEP_LEVEL_RE.match(module_name) is not None


def classify_general_import_from(
    module_name: str, current_level: int
) -> tuple[str, int] | None:
    """Classify level import module against current level."""
    match = LEVEL_DIR_RE.fullmatch(module_name)
    if not match:
        return None
    imported_level = int(match.group(1))
    if imported_level == current_level:
        return ("WRONG_LEVEL", imported_level)
    if imported_level > current_level:
        return ("UPWARD", imported_level)
    return None


__all__ = ["has_deep_level_path", "classify_general_import_from"]
