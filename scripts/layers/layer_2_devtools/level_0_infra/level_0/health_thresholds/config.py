"""Threshold numbers for code health checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ThresholdConfig:
    """Configurable limits for health metrics (defaults are sane out of the box)."""

    max_file_lines: int = 500
    max_function_lines: int = 50
    max_class_methods: int = 7
    max_function_complexity: int = 10
    max_class_complexity: int = 50
    min_package_cohesion_pct: int = 25
    max_deep_imports: int = 30
    max_import_depth: int = 4
    max_duplicate_blocks: int = 200
    min_duplicate_lines: int = 6
    min_duplicate_frequency_for_warning: int = 3
    max_actionable_duplicate_blocks: int = 30
    max_unused_imports: int = 0
    max_unreachable_blocks: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_file_lines": self.max_file_lines,
            "max_function_lines": self.max_function_lines,
            "max_class_methods": self.max_class_methods,
            "max_function_complexity": self.max_function_complexity,
            "max_class_complexity": self.max_class_complexity,
            "min_package_cohesion_pct": self.min_package_cohesion_pct,
            "max_deep_imports": self.max_deep_imports,
            "max_import_depth": self.max_import_depth,
            "max_duplicate_blocks": self.max_duplicate_blocks,
            "min_duplicate_lines": self.min_duplicate_lines,
            "min_duplicate_frequency_for_warning": getattr(
                self, "min_duplicate_frequency_for_warning", 3
            ),
            "max_actionable_duplicate_blocks": getattr(
                self, "max_actionable_duplicate_blocks", 30
            ),
            "max_unused_imports": self.max_unused_imports,
            "max_unreachable_blocks": self.max_unreachable_blocks,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ThresholdConfig:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


__all__ = ["ThresholdConfig"]
