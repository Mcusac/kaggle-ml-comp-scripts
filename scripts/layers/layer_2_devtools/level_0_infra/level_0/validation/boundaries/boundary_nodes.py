"""Package boundary nodes used by boundary validation and reporting.

These nodes are intentionally coarse-grained: they represent *policy boundaries*
and not individual Python packages/modules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundaryNode:
    """A boundary node in the matrix (stable key + human label + ordering)."""

    key: str
    label: str
    sort_key: tuple

    def to_dict(self) -> dict[str, object]:
        return {"key": self.key, "label": self.label, "sort_key": list(self.sort_key)}

