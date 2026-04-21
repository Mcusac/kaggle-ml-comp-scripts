from __future__ import annotations

from pathlib import Path

from layers.layer_2_devtools.level_1_impl.level_0.regenerate_inits.apply import compute_drift
from layers.layer_2_devtools.level_1_impl.level_0.regenerate_inits.apply import (
    expected_init_for_package,
)
from layers.layer_2_devtools.level_1_impl.level_0.regenerate_inits.public_symbols import (
    public_symbols_from_module,
)


def test_public_symbols_from_module_ast_rules() -> None:
    src = """
import os
from x import y

CONST = 1
_PRIVATE_CONST = 2

X: int = 3
_Y: int = 4

def f():
    return 1

async def af():
    return 2

class C:
    pass

def _hidden():
    return 0
"""
    assert public_symbols_from_module(src) == ["C", "CONST", "X", "af", "f"]


def test_expected_init_leaf_package(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()

    (root / "__init__.py").write_text("", encoding="utf-8")
    (root / "a.py").write_text(
        """
class A:
    pass

def f():
    return 1

_x = 1
""",
        encoding="utf-8",
    )
    (root / "b.py").write_text("CONST = 1\n", encoding="utf-8")
    (root / "empty.py").write_text("_x = 1\n", encoding="utf-8")

    rendered = expected_init_for_package(root, include_tests=False)
    assert rendered.kind == "leaf"
    assert "from .a import" in rendered.text
    assert "from .b import CONST" in rendered.text
    assert ".empty" not in rendered.text
    assert '"A"' in rendered.text
    assert '"f"' in rendered.text
    assert '"CONST"' in rendered.text


def test_expected_init_aggregate_package(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "__init__.py").write_text("", encoding="utf-8")

    sub = root / "sub"
    sub.mkdir()
    (sub / "__init__.py").write_text("", encoding="utf-8")
    (sub / "m.py").write_text("def g():\n    return 1\n", encoding="utf-8")

    rendered_root = expected_init_for_package(root, include_tests=False)
    assert rendered_root.kind == "aggregate"
    assert "from . import sub" in rendered_root.text
    assert "from .sub import *" in rendered_root.text
    assert "__all__ = list(sub.__all__)" in rendered_root.text

    rendered_sub = expected_init_for_package(sub, include_tests=False)
    assert rendered_sub.kind in {"leaf", "stub"}


def test_compute_drift_includes_missing_init(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    drifts = compute_drift(root, include_tests=False)
    init_drift = [d for d in drifts if d.init_path == root / "__init__.py"]
    assert init_drift
    assert init_drift[0].expected

