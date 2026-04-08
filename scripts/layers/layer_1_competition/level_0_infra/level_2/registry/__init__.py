"""Contest CLI handler registry surface (tier 2).

This tier owns CLI handler module resolution because it depends on tier 1's
ContestRegistry.
"""

from .cli_handlers import (
    get_cli_handlers_module,
    list_contests_with_cli_handlers,
    register_cli_handlers_module,
)

__all__ = [
    "get_cli_handlers_module",
    "list_contests_with_cli_handlers",
    "register_cli_handlers_module",
]

