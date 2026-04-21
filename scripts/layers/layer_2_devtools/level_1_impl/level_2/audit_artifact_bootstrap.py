"""Load ``level_0.path.workspace`` from file path (no ``layers...level_0_infra`` package init).

`level_0_infra` / ``level_0`` package ``__init__`` can import heavy optional deps. Precheck
skip-stub and schema checks only need stdlib path helpers from ``workspace.py``."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable

_workspace_py: Path = (
    Path(__file__).resolve().parents[2] / "level_0_infra" / "level_0" / "path" / "workspace.py"
)
_resolve: Callable[[Path], Path] | None = None


def get_resolve_audit_artifact_root() -> Callable[[Path], Path]:
    """Return ``resolve_audit_artifact_root`` (same implementation as in ``workspace.py``)."""
    global _resolve
    if _resolve is not None:
        return _resolve
    name = "devtools_path_workspace_bootstrap"
    spec = importlib.util.spec_from_file_location(name, _workspace_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load path helpers from {_workspace_py}")
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _resolve = mod.resolve_audit_artifact_root
    return _resolve
