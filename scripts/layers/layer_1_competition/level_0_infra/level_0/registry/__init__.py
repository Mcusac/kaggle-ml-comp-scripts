"""Generic registries for contest implementations (infra-level).

This is **not** the contest registry (`level_0_infra.level_1.registry`).
It is for small runtime registries like model/trainers, keyed by string names.
"""

from layers.layer_0_core.level_0 import NamedRegistry, build_unknown_key_error

__all__ = [
    "NamedRegistry",
    "build_unknown_key_error",
]

