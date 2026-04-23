"""Re-export: canonical general-stack import rules live in level_0.validation.import_rules."""

from layers.layer_2_devtools.level_0_infra.level_0.validation.import_rules.general_rules import (
    classify_general_import_from,
    has_deep_level_path,
)

__all__ = [
    "classify_general_import_from",
    "has_deep_level_path",
]
