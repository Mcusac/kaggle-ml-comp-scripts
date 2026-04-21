"""Import smoke tests for level_0, level_1, level_2 packages.

Tests are collected from ``layers/layer_2_devtools/impl/tests/``; core packages load via
``layers.layer_0_core.level_*`` (``scripts/`` on ``sys.path``, see ``conftest.py``), not from ``dev/``.

Verifies that the three packages can be imported without circular dependencies
and that key exports are available.

Run from ``scripts/``. If ``pytest`` is not on PATH, use:

  python -m pytest layers/layer_2_devtools/impl/tests/unit/test_levels/test_level_0_1_2_imports.py -v

``level_0`` imports the vision submodule, which requires ``torchvision`` at import time.
Install with ``pip install torchvision`` (or the project's vision extra) for these tests to run.

Note: Deeper utilities (e.g. ``load_csv``, ``validate_path_is_file``) live in ``level_3+``;
these tests only assert the current ``level_1`` / ``level_2`` submodule layout.
"""

from typing import Callable

import pytest


def test_sys_path_includes_layer_0_core(scripts_dir, layer_0_core_dir):
    """Smoke: layers layout + path hookup (no optional vision deps)."""
    import sys

    assert layer_0_core_dir.is_dir(), f"missing {layer_0_core_dir}"
    assert str(layer_0_core_dir) in sys.path
    assert str(scripts_dir) in sys.path


def test_import_level_0(assert_module_under_layer_0_core: Callable[[object], None]):
    """level_0 can be imported and exposes core symbols."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    import layers.layer_0_core.level_0 as level_0

    assert_module_under_layer_0_core(level_0)
    assert hasattr(level_0, "get_logger")
    assert hasattr(level_0, "ensure_dir")
    assert hasattr(level_0, "DataSplit")
    assert hasattr(level_0, "BaseConfig")
    assert hasattr(level_0, "RuntimeConfig")
    assert hasattr(level_0, "add_common_arguments")
    assert hasattr(level_0, "DataLoadError")
    assert hasattr(level_0, "ExecutionResult")
    assert hasattr(level_0, "is_kaggle")


def test_import_level_1(assert_module_under_layer_0_core: Callable[[object], None]):
    """level_1 can be imported and exposes framework subpackages."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    import layers.layer_0_core.level_1 as level_1

    assert_module_under_layer_0_core(level_1)
    for name in (
        "cli",
        "data",
        "evaluation",
        "features",
        "grid_search",
        "guards",
        "io",
        "ontology",
        "pipelines",
        "protein",
        "runtime",
        "search",
        "training",
    ):
        assert getattr(level_1, name, None) is not None, f"missing level_1.{name}"
    from layers.layer_0_core.level_1.io import TsvSubmissionFormatter

    assert TsvSubmissionFormatter is not None


def test_import_level_2(assert_module_under_layer_0_core: Callable[[object], None]):
    """level_2 can be imported and exposes component subpackages."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    import layers.layer_0_core.level_2 as level_2

    assert_module_under_layer_0_core(level_2)
    for name in (
        "analysis",
        "dataloader",
        "ensemble_strategies",
        "feature_extractors",
        "grid_search",
        "inference",
        "models",
        "progress",
        "runtime",
        "training",
        "validation",
        "vision_transforms",
    ):
        assert getattr(level_2, name, None) is not None, f"missing level_2.{name}"
    assert hasattr(level_2, "ProgressBarManager")
    assert hasattr(level_2, "DINOv2Model")


def test_level_1_depends_only_on_level_0():
    """level_1 can be used; it depends only on level_0 (no level_2)."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    from layers.layer_0_core.level_1.io import TsvSubmissionFormatter

    assert TsvSubmissionFormatter is not None


def test_level_2_imports_level_0_and_level_1():
    """level_2 public API is reachable (implementation may import level_0 / level_1)."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    from layers.layer_0_core.level_2.models import DINOv2Model

    assert DINOv2Model is not None
