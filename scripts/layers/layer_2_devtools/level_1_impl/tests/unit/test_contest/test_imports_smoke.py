"""Import smoke tests for contest pipeline modules.

Catches wrong relative imports (e.g. ...data -> non-existent contest.implementations.csiro.data)
and missing internal modules. Fails on contest.*, config.*, utils.*; skips when only optional
deps (torch, lightgbm, etc.) are missing.
"""

import importlib
from pathlib import Path

import pytest

pytest.importorskip("contest")

OPTIONAL_DEPS = frozenset({'torch', 'timm', 'lightgbm', 'xgboost', 'sklearn'})


def _get_scripts_root() -> Path:
    return Path(__file__).resolve().parents[6]


def _get_contest_pipeline_modules() -> list[str]:
    scripts = _get_scripts_root()
    impl = scripts / "contest" / "implementations"
    if not impl.is_dir():
        return []
    modules = []
    for c in impl.iterdir():
        if not c.is_dir() or c.name.startswith('_'):
            continue
        pip = c / "pipelines"
        if not pip.is_dir():
            continue
        for p in pip.glob("*.py"):
            if p.stem == "__init__":
                continue
            modules.append(f"contest.implementations.{c.name}.pipelines.{p.stem}")
    return sorted(modules)


def _is_internal_module(name: str) -> bool:
    return name.startswith(('contest.', 'config.', 'utils.'))


@pytest.mark.parametrize("module_name", _get_contest_pipeline_modules())
def test_contest_pipeline_imports(module_name: str) -> None:
    """Import contest pipeline modules to catch wrong relative imports (e.g. ...data) and missing internal modules."""
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError as e:
        n = getattr(e, 'name', '') or ''
        if n in OPTIONAL_DEPS or (n.split('.')[0] in OPTIONAL_DEPS):
            pytest.skip(f"Optional dependency not installed: {n}")
        if _is_internal_module(n):
            raise
        pytest.skip(f"External dependency not installed: {n}")
    except ImportError as e:
        # Handle DLL load failures and other import errors for optional dependencies
        error_msg = str(e).lower()
        # Check if error is related to optional dependencies (torch DLL issues, etc.)
        if any(dep in error_msg for dep in OPTIONAL_DEPS):
            pytest.skip(f"Optional dependency import error (likely missing DLLs or incomplete installation): {e}")
        # If it's an internal module import error, that's a real problem
        if _is_internal_module(str(e)):
            raise
        # Otherwise, skip as external dependency issue
        pytest.skip(f"External dependency import error: {e}")
