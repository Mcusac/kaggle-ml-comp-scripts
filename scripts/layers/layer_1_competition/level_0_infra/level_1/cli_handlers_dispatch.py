"""Map contest name to CLI handlers module (extend_subparsers / get_handlers)."""

import importlib
from types import ModuleType
from typing import Dict, List

_CLI_HANDLERS_MODULES: Dict[str, str] = {}


def list_contests_with_cli_handlers() -> List[str]:
    """Contest keys that registered a handlers module."""
    return sorted(_CLI_HANDLERS_MODULES.keys())


def get_cli_handlers_module(contest: str) -> ModuleType:
    """
    Import and return the handlers module for ``contest``.

    If unregistered, imports ``layers.layer_1_competition.level_1_impl.level_{contest}.registration``
    once (same convention as notebook command dispatch).
    """
    key = (contest or "").strip().lower()
    mod_path = _CLI_HANDLERS_MODULES.get(key)
    if mod_path is None:
        try:
            importlib.import_module(
                f"layers.layer_1_competition.level_1_impl.level_{key}.registration"
            )
        except ModuleNotFoundError:
            pass
        mod_path = _CLI_HANDLERS_MODULES.get(key)
    if mod_path is None:
        available = ", ".join(list_contests_with_cli_handlers()) or "(none)"
        raise ValueError(
            f"No CLI handlers module registered for contest {contest!r}. "
            f"Available: {available}"
        )
    return importlib.import_module(mod_path)


def register_cli_handlers_module(contest: str, module_path: str) -> None:
    """Register dotted import path for contest CLI handlers (from each contest ``registration.py``)."""
    _CLI_HANDLERS_MODULES[contest.strip().lower()] = module_path
