"""Competition layer: shared ``level_0_infra`` and per-contest ``level_1_impl``.

Import infrastructure from ``layers.layer_1_competition.level_0_infra``. Contest code
lives under ``layers.layer_1_competition.level_1_impl.level_<contest>``; each contest's
``registration.py`` registers with ``ContestRegistry`` and CLI/notebook dispatch when
imported (typically via dispatch or ``run.py`` preload), not via this package root.

``path_bootstrap.prepend_framework_paths()`` prepends ``scripts/`` so ``layers.*`` resolves.
"""

from . import level_0_infra

from .level_0_infra import *

__all__ = tuple(level_0_infra.__all__)
