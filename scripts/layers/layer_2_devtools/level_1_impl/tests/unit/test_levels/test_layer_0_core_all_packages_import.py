"""Import every general-stack package under ``layer_0_core`` (``level_0`` … ``level_10``).

Tests live under ``layers/layer_2_devtools/impl/tests/`` for discovery only; assertions touch
``scripts/layers/layer_0_core`` on disk and import ``level_*`` from there.

Run from ``scripts/``:

  python -m pytest layers/layer_2_devtools/impl/tests/unit/test_levels/test_layer_0_core_all_packages_import.py -v

- **Directory checks:** one parametrized test per ``level_N`` (always runs).
- **Import check:** a **single** test that imports all packages in order. It is skipped **once**
  if optional deps (typically ``torchvision`` / ``torch``) are missing, instead of eleven
  identical skips.

Install vision stack to exercise imports: ``pip install torch torchvision`` (or your env’s extras).
"""

import importlib
from pathlib import Path
from typing import Callable

import pytest


@pytest.mark.parametrize("n", range(11))
def test_level_n_package_dir_exists(n: int, layer_0_core_dir: Path) -> None:
    root = layer_0_core_dir / f"level_{n}"
    assert root.is_dir(), f"expected package dir: {root}"
    assert (root / "__init__.py").is_file(), f"missing __init__.py under {root}"


def test_all_level_packages_import(
    assert_module_under_layer_0_core: Callable[[object], None],
) -> None:
    """Import ``level_0`` … ``level_10`` (one failure surfaces the first broken level)."""
    pytest.importorskip("torchvision", reason="core stack imports load level_0 vision")
    pytest.importorskip("torch", reason="vision/torch stack")

    for n in range(11):
        name = f"level_{n}"
        mod = importlib.import_module(name)
        assert mod.__name__ == name, f"{name!r} resolved wrong module"
        assert_module_under_layer_0_core(mod)
