"""Contest implementations under ``layer_1_competition/level_1_impl/``.

Each child package (``level_cafa``, ``level_csiro``, …) has its own ``level_0`` … ``level_K``
tree. Import a contest subpackage explicitly (e.g. ``level_arc_agi_2.level_0``). Do **not**
import every contest from this ``__init__`` — optional third-party deps (Bio, unsloth, …)
would force-install for all workflows.

``registration`` modules are loaded by ``run_helpers.preload_contest_registrations`` / CLI
so only the selected contest is imported.
"""

__all__ = ["level_arc_agi_2", "level_cafa", "level_csiro", "level_rna3d"]
