"""Map contest name to ``notebook_commands`` module (lazy import).

The dispatch map starts empty. Each contest calls
:func:`register_notebook_commands_module` from its own ``registration.py``
so this infra module has no hard dependency on any contest package.
"""

import importlib
from types import ModuleType
from typing import Dict, List


_NOTEBOOK_COMMAND_MODULES: Dict[str, str] = {}


def list_contests_with_notebook_commands() -> List[str]:
    """Return contest keys that have a ``notebook_commands`` module registered."""
    return sorted(_NOTEBOOK_COMMAND_MODULES.keys())


def get_notebook_commands_module(contest: str) -> ModuleType:
    """Import and return the ``notebook_commands`` module for ``contest``.

    If the contest is not yet in the dispatch map, imports
    ``layers.layer_1_competition.level_1_impl.level_{contest}.registration`` once
    (convention: package ``level_cafa``, ``level_csiro``, ``level_rna3d``) so
    notebook flows load only that contest's registration side effects.

    Args:
        contest: Registry contest name (e.g. ``rna3d``, ``csiro``).

    Raises:
        ValueError: If ``contest`` is unknown.
        ModuleNotFoundError: If the mapped module cannot be imported.
    """
    key = (contest or "").strip().lower()
    mod_path = _NOTEBOOK_COMMAND_MODULES.get(key)
    if mod_path is None:
        try:
            importlib.import_module(
                f"layers.layer_1_competition.level_1_impl.level_{key}.registration"
            )
        except ModuleNotFoundError:
            pass
        mod_path = _NOTEBOOK_COMMAND_MODULES.get(key)
    if mod_path is None:
        available = ", ".join(list_contests_with_notebook_commands()) or "(none)"
        raise ValueError(
            f"No notebook_commands registered for contest {contest!r}. "
            f"Available: {available}"
        )
    return importlib.import_module(mod_path)


def register_notebook_commands_module(contest: str, module_path: str) -> None:
    """Register the ``notebook_commands`` import path for a contest.

    Called from each contest's ``registration.py`` as a side effect, keeping
    infra free of direct references to contest packages.
    """
    _NOTEBOOK_COMMAND_MODULES[contest.strip().lower()] = module_path
