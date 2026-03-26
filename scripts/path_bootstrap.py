"""Prepend framework directories on ``sys.path``.

General stack packages live under ``layers/layer_0_core/`` (top-level ``level_*``).
Competition code imports via ``layers.layer_1_competition.level_0_infra`` and
``layers.layer_1_competition.level_1_impl`` — no ``scripts/level_C/`` junctions.

A fresh subprocess that runs ``run.py`` (e.g. from a notebook via
``run_cli_streaming``) does not execute notebook imports; ``run.py`` calls
``preload_contest_registrations`` so ``ContestRegistry`` and CLI handler maps
are populated. If ``--contest`` or ``KAGGLE_COMP_CONTEST`` is set, only that
contest's ``registration`` is imported; otherwise all known contests are tried.
"""

import os
import sys
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path(__file__).resolve().parent
_LAYER_0_CORE = _SCRIPTS_DIR / "layers" / "layer_0_core"


def prepend_framework_paths(*, ensure_level_c: bool = True) -> None:
    """Put ``layer_0_core`` and ``scripts/`` first on ``sys.path``.

    ``ensure_level_c`` is ignored (kept for backward-compatible call sites).
    """
    del ensure_level_c  # deprecated; junction layout removed
    for p in (_LAYER_0_CORE, _SCRIPTS_DIR):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)


def resolve_notebook_scripts_path(scripts_package: str = "kaggle-ml-comp-scripts") -> str:
    """Resolve ``.../scripts`` for a Kaggle input dataset (stdlib only; no imports from ``layers``)."""
    is_kaggle = os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "") != ""
    if is_kaggle:
        return f"/kaggle/input/{scripts_package}/scripts"
    cand = f"../input/{scripts_package}/scripts"
    alt = f"../{scripts_package}/scripts"
    return cand if os.path.isdir(cand) else alt


def bootstrap_notebook_environment(
    *,
    contest: Optional[str] = None,
    scripts_package: str = "kaggle-ml-comp-scripts",
) -> str:
    """Insert scripts package path, prepend framework paths, optional ``KAGGLE_COMP_CONTEST``.

    Notebooks should run: ``sys.path.insert(0, resolve_notebook_scripts_path(...))`` then
    ``from path_bootstrap import bootstrap_notebook_environment`` and call this function,
    then import from ``layers...``.
    """
    scripts_path = resolve_notebook_scripts_path(scripts_package)
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    prepend_framework_paths()
    if contest is not None:
        os.environ.setdefault("KAGGLE_COMP_CONTEST", contest)
    return scripts_path
