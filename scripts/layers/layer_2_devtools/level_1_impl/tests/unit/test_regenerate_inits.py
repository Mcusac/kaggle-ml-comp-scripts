from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent


def _load_regenerate_inits():
    pkg_dir = (_SCRIPT_DIR.parents[1] / "level_0" / "regenerate_inits").resolve()
    init_path = pkg_dir / "__init__.py"
    if not init_path.exists():
        raise FileNotFoundError(f"regenerate_inits __init__.py not found: {init_path}")

    pkg_name = "_kaggle_ml_regenerate_inits_for_tests"
    spec = importlib.util.spec_from_file_location(
        pkg_name,
        init_path,
        submodule_search_locations=[str(pkg_dir)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to create module spec for {init_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[pkg_name] = module
    spec.loader.exec_module(module)
    return module


_regen = _load_regenerate_inits()
compute_drift = _regen.compute_drift
expected_init_for_package = _regen.expected_init_for_package
report_nonlocal_imports = _regen.report_nonlocal_imports
public_symbols_from_module = _regen.public_symbols_from_module


def test_public_symbols_from_module_ast_rules() -> None:
    src = """
import os
from x import y

def main():
    return 0

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


def test_public_symbols_exclude_can_allow_main() -> None:
    src = """
def main():
    return 0
"""
    assert public_symbols_from_module(src, exclude=set()) == ["main"]


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


def test_expected_init_mixed_package(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "__init__.py").write_text("", encoding="utf-8")

    (root / "m.py").write_text(
        """
def f():
    return 1
""",
        encoding="utf-8",
    )

    sub = root / "sub"
    sub.mkdir()
    (sub / "__init__.py").write_text("", encoding="utf-8")
    (sub / "a.py").write_text("CONST = 1\n", encoding="utf-8")

    rendered = expected_init_for_package(root, include_tests=False)
    assert rendered.kind == "mixed"
    assert "from . import sub" in rendered.text
    assert "from .sub import *" in rendered.text
    assert "from .m import f" in rendered.text
    assert "list(sub.__all__)" in rendered.text
    assert '"f"' in rendered.text


def test_compute_drift_includes_missing_init(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")

    drifts = compute_drift(root, include_tests=False)
    init_drift = [d for d in drifts if d.init_path == root / "__init__.py"]
    assert init_drift
    assert init_drift[0].expected


def test_report_nonlocal_imports_flags_absolute_imports(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "__init__.py").write_text("import os\n", encoding="utf-8")
    assert report_nonlocal_imports(root, include_tests=False) == [root / "__init__.py"]


def test_report_nonlocal_imports_allows_relative_imports(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    root.mkdir()
    (root / "__init__.py").write_text("from .a import X\n", encoding="utf-8")
    (root / "a.py").write_text("X = 1\n", encoding="utf-8")
    assert report_nonlocal_imports(root, include_tests=False) == []

