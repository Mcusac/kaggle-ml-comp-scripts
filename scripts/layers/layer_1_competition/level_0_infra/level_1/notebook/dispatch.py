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

    This module intentionally does not import contest implementations. Callers must
    import the contest's ``registration`` module first to populate this dispatch map.

    Args:
        contest: Registry contest name (e.g. ``rna3d``, ``csiro``).

    Raises:
        ValueError: If ``contest`` is unknown.
        ModuleNotFoundError: If the mapped module cannot be imported.
    """
    key = (contest or "").strip().lower()
    mod_path = _NOTEBOOK_COMMAND_MODULES.get(key)
    if mod_path is None:
        available = ", ".join(list_contests_with_notebook_commands()) or "(none)"
        raise ValueError(
            f"No notebook_commands registered for contest {contest!r}. "
            f"Available: {available}. "
            f"Import `layers.layer_1_competition.level_1_impl.level_{key}.registration` first."
        )
    return importlib.import_module(mod_path)


def register_notebook_commands_module(contest: str, module_path: str) -> None:
    """Register the ``notebook_commands`` import path for a contest.

    Called from each contest's ``registration.py`` as a side effect, keeping
    infra free of direct references to contest packages.
    """
    _NOTEBOOK_COMMAND_MODULES[contest.strip().lower()] = module_path
