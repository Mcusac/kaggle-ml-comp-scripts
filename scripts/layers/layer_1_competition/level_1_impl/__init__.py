"""Contest implementations under ``layer_1_competition/level_1_impl/``.

Each child package (``level_cafa``, ``level_csiro``, ``level_rna3d``) has its own
``level_0`` … ``level_K`` tree. Import as ``layers.layer_1_competition.level_1_impl.<name>``.

Importing a subpackage runs its ``registration`` module.
"""

import importlib
from typing import Any

_LAZY_CONTEST_SUBPACKAGES = frozenset(
    {"level_arc_agi_2", "level_cafa", "level_csiro", "level_rna3d"}
)

__all__ = ["level_arc_agi_2", "level_cafa", "level_csiro", "level_rna3d"]


def __getattr__(name: str) -> Any:
    if name in _LAZY_CONTEST_SUBPACKAGES:
        return importlib.import_module(f"{__name__}.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
