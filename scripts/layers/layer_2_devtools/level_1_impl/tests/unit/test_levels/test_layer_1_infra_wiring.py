"""Wiring: ``layer_1_competition/level_0_infra`` and ``layer_0_core`` ``level_*``.

``path_bootstrap.prepend_framework_paths()`` prepends ``layer_0_core`` and ``scripts/``
on ``sys.path``. Competition infra imports as ``layers.layer_1_competition.level_0_infra.level_N``.
General stack symbols import as ``layers.layer_0_core.level_N`` (or legacy top-level ``level_*`` when using bootstrap-only paths).
"""

import importlib
from typing import Callable

import pytest


def test_import_infra_stack_with_core_resolution(
    assert_module_under_layer_0_core: Callable[[object], None],
    assert_module_under_infra: Callable[[object, str], None],
) -> None:
    """Import competition infra ``level_0``…``level_4``; core via ``layers.layer_0_core.level_0``."""
    pytest.importorskip("torchvision", reason="core level_0 pulls vision at import")
    pytest.importorskip("torch", reason="vision stack")

    import layers.layer_0_core.level_0 as core_level_0

    assert_module_under_layer_0_core(core_level_0)

    for i in range(5):
        name = f"layers.layer_1_competition.level_0_infra.level_{i}"
        mod = importlib.import_module(name)
        assert mod.__name__ == name
        assert_module_under_infra(mod, f"level_{i}")

    import layers.layer_1_competition.level_0_infra.level_1 as c1

    assert hasattr(c1, "get_command_handlers")
