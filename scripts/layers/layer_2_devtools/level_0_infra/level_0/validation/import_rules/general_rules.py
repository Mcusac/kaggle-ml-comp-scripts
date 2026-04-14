"""General-stack import rule helpers for devtools scanners."""

import re

_LEVEL_RE = re.compile(r"^level_(\d+)$")


def has_deep_level_path(module_name: str) -> bool:
    """True when import-from module is `level_N.something` (deep path)."""
    if not module_name.startswith("level_"):
        return False
    return "." in module_name and bool(_LEVEL_RE.fullmatch(module_name.split(".", 1)[0]))


def classify_general_import_from(module_name: str, current_level: int) -> str | None:
    """
    Classify `from <module_name> import ...` for general stack logic files.

    Returns:
      - "WRONG_LEVEL" when importing from same level (`level_current`)
      - "UPWARD_VIOLATION" when importing from higher level (`level_X`, X > current)
      - None otherwise (not a general level import, or lower-level import)
    """
    match = _LEVEL_RE.fullmatch(module_name)
    if not match:
        return None
    imported_level = int(match.group(1))
    if imported_level == current_level:
        return "WRONG_LEVEL"
    if imported_level > current_level:
        return "UPWARD_VIOLATION"
    return None