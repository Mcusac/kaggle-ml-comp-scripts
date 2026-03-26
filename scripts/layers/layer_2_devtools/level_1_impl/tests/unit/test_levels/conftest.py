"""Shared paths for layer stack import tests.

Pytest discovers tests under ``layers/layer_2_devtools/impl/tests/``, but the **code under test**
lives under ``scripts/layers/`` (``layer_0_core`` general stack and ``layer_1_competition/level_0_infra``).
Uses ``path_bootstrap.prepend_framework_paths()`` — same as ``run.py`` — so
``level_*`` resolves to core and ``layers.layer_1_competition.*`` resolves to
competition packages.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pytest

_THIS_FILE = Path(__file__).resolve()
# conftest.py -> test_levels -> unit -> tests -> impl -> layer_2_devtools -> layers -> scripts
_SCRIPTS_DIR = _THIS_FILE.parents[6]
_LAYER_0_CORE = _SCRIPTS_DIR / "layers" / "layer_0_core"
_LAYER_1_INFRA = _SCRIPTS_DIR / "layers" / "layer_1_competition" / "infra"

if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from path_bootstrap import prepend_framework_paths

prepend_framework_paths()


@pytest.fixture(scope="session")
def scripts_dir() -> Path:
    return _SCRIPTS_DIR


@pytest.fixture(scope="session")
def layer_0_core_dir() -> Path:
    return _LAYER_0_CORE


@pytest.fixture(scope="session")
def layer_1_infra_dir() -> Path:
    return _LAYER_1_INFRA


@pytest.fixture(scope="session")
def assert_module_under_layer_0_core(
    layer_0_core_dir: Path,
) -> Callable[[object], None]:
    """Callable that fails if a module was not imported from ``layer_0_core``."""

    root = layer_0_core_dir.resolve()

    def _check(mod: object) -> None:
        f = getattr(mod, "__file__", None)
        assert f, f"{getattr(mod, '__name__', mod)!r} has no __file__"
        path = Path(f).resolve()
        assert path.is_relative_to(root), (
            f"expected {getattr(mod, '__name__', mod)!r} under {root}, got {path}"
        )

    return _check


@pytest.fixture(scope="session")
def assert_module_under_infra(
    layer_1_infra_dir: Path,
) -> Callable[[object, str], None]:
    """Assert ``mod.__file__`` lies under ``infra/<level_subdir>/`` (e.g. ``level_0``)."""

    infra_root = layer_1_infra_dir.resolve()

    def _check(mod: object, level_subdir: str) -> None:
        f = getattr(mod, "__file__", None)
        assert f, f"{getattr(mod, '__name__', mod)!r} has no __file__"
        path = Path(f).resolve()
        expected = (infra_root / level_subdir).resolve()
        assert path.is_relative_to(expected), (
            f"expected {getattr(mod, '__name__', mod)!r} under {expected}, got {path}"
        )

    return _check
