"""Competition infra level 0: contest-facing base types and helpers."""

from . import (
    abstractions,
    artifacts,
    cli,
    model,
    paths,
    pipeline,
    submission,
)

from . import argv_command_builders

from .handler_context import setup_handler_context

from .abstractions import *
from .artifacts import *
from .argv_command_builders import *
from .cli import *
from .model import *
from .paths import *
from .pipeline import *
from .submission import *

__all__ = (
    list(abstractions.__all__)
    + list(artifacts.__all__)
    + list(argv_command_builders.__all__)
    + list(cli.__all__)
    + list(model.__all__)
    + list(paths.__all__)
    + list(pipeline.__all__)
    + list(submission.__all__)
    + ["setup_handler_context"]
)
