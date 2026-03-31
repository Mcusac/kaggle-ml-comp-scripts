"""Contest implementations under ``layer_1_competition/level_1_impl/``.

Each child package (``level_cafa``, ``level_csiro``, ``level_rna3d``) has its own
``level_0`` … ``level_K`` tree. Import as ``layers.layer_1_competition.level_1_impl.<name>``.

Importing a subpackage runs its ``registration`` module.
"""

from . import level_arc_agi_2, level_cafa, level_csiro, level_rna3d

__all__ = ["level_arc_agi_2", "level_cafa", "level_csiro", "level_rna3d"]
