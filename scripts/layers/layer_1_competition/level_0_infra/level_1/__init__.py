"""Competition infra tier 1: feature extraction, export, handlers, paths."""

from . import (
    contest,
    export,
    features,
    grid_search,
    handlers,
    notebook,
    paths,
    registry,
)

from .cli_handlers_dispatch import (
    get_cli_handlers_module,
    list_contests_with_cli_handlers,
    register_cli_handlers_module,
)
from .contest import *
from .export import *
from .features import *
from .grid_search import *
from .handlers import *
from .notebook import *
from .paths import *
from .registry import *

__all__ = (
    [
        "get_cli_handlers_module",
        "list_contests_with_cli_handlers",
        "register_cli_handlers_module",
    ]
    + list(contest.__all__)
    + list(export.__all__)
    + list(features.__all__)
    + list(grid_search.__all__)
    + list(handlers.__all__)
    + list(notebook.__all__)
    + list(paths.__all__)
    + list(registry.__all__)
)