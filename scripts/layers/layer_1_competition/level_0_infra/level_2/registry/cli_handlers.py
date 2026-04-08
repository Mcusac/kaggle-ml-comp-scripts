"""Contest CLI handler module registry (stored in ContestRegistry entries)."""

import importlib

from types import ModuleType
from typing import List

from layers.layer_1_competition.level_0_infra.level_1 import ContestRegistry


def register_cli_handlers_module(contest: str, module_path: str) -> None:
    """
    Register dotted import path for contest CLI handlers (from each contest `registration.py`).
    """
    key = (contest or "").strip().lower()
    if not key:
        raise ValueError("contest must be non-empty")
    entry = ContestRegistry.get(key)
    if entry is None:
        raise ValueError(f"Contest {contest!r} must be registered before registering CLI handlers")
    entry["cli_handlers_module"] = str(module_path)


def list_contests_with_cli_handlers() -> List[str]:
    """Contest keys that registered a handlers module."""
    out: List[str] = []
    for name in ContestRegistry.list_contests():
        entry = ContestRegistry.get(name) or {}
        if entry.get("cli_handlers_module"):
            out.append(name)
    return sorted(out)


def get_cli_handlers_module(contest: str) -> ModuleType:
    """
    Import and return the handlers module for `contest`.

    This module intentionally does not import contest implementations. Callers must
    import the contest's `registration` module first to populate ContestRegistry.
    """
    key = (contest or "").strip().lower()
    entry = ContestRegistry.get(key) or {}
    mod_path = entry.get("cli_handlers_module")
    if not mod_path:
        available = ", ".join(list_contests_with_cli_handlers()) or "(none)"
        raise ValueError(
            f"No CLI handlers module registered for contest {contest!r}. "
            f"Available: {available}. "
            f"Import `layers.layer_1_competition.level_1_impl.level_{key}.registration` first."
        )
    return importlib.import_module(str(mod_path))

