"""Import smoke tests for level_0, level_1, level_2 packages.

Tests are collected from ``layers/layer_2_devtools/impl/tests/``; core packages load via
``layers.layer_0_core.level_*`` (``scripts/`` on ``sys.path``, see ``conftest.py``), not from ``dev/``.

Verifies that the three packages can be imported without circular dependencies
and that key exports are available.

Run from ``scripts/``. If ``pytest`` is not on PATH, use:

  python -m pytest layers/layer_2_devtools/impl/tests/unit/test_levels/test_level_0_1_2_imports.py -v

``level_0`` imports the vision submodule, which requires ``torchvision`` at import time.
Install with ``pip install torchvision`` (or the project's vision extra) for these tests to run.
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
    assert level_1.batch_loading is not None
    assert level_1.builders is not None
    assert level_1.data_processing is not None
    assert level_1.data_structure is not None
    assert level_1.execution is not None
    assert level_1.progress is not None
    assert level_1.reporting is not None
    assert level_1.runtime is not None
    assert level_1.validation is not None
    # Optional subpackages may be None
    from layers.layer_0_core.level_1.validation import validate_path_is_file
    assert callable(validate_path_is_file)


def test_import_level_2(assert_module_under_layer_0_core: Callable[[object], None]):
    """level_2 can be imported and exposes component subpackages."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    import layers.layer_0_core.level_2 as level_2

    assert_module_under_layer_0_core(level_2)
    assert level_2.file_io is not None
    assert level_2.progress_formatting is not None
    assert level_2.metrics is not None
    # Optional subpackages may be None if torch/etc. missing
    assert hasattr(level_2, "load_csv")
    assert hasattr(level_2, "ProgressFormatter")
    assert hasattr(level_2, "calculate_accuracy")


def test_level_1_depends_only_on_level_0():
    """level_1 can be used; it depends only on level_0 (no level_2)."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    from layers.layer_0_core.level_1 import validation
    assert validation is not None
    from layers.layer_0_core.level_1.validation import validate_path_is_file
    assert callable(validate_path_is_file)


def test_level_2_imports_level_0_and_level_1():
    """level_2 file_io uses level_0 and level_1."""
    pytest.importorskip("torchvision", reason="level_0 loads vision at import")
    from layers.layer_0_core.level_2.file_io import load_csv
    assert callable(load_csv)
