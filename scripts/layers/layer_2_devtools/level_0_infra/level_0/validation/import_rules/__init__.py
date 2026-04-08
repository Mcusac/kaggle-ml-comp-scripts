"""Import-rule classifiers for devtools scans."""

from .general_rules import classify_general_import_from, has_deep_level_path

__all__ = ["classify_general_import_from", "has_deep_level_path"]

