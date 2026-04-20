"""ARC-AGI-2 contest implementation package.

Heavy subgraph (``level_0`` … ``level_8``) is not imported at package load time so
``registration`` can run under ``run.py`` without optional training deps (e.g. unsloth).
Import subpackages explicitly (e.g. ``level_arc_agi_2.level_0.config``).
"""

__all__: list[str] = []
