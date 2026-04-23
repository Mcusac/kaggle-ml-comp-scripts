"""
Top-level `layers` package.

We intentionally do not eagerly import the entire `layers.*` tree here:
- importing subpackages can pull in optional dependencies
- importing cross-layer entrypoints can trigger unrelated import-time failures

Callers should import the specific subpackage they need, e.g.:
`from layers.layer_0_core.level_2 import ...`.
"""

__all__: list[str] = []
