"""Auto-generated mixed exports."""


from . import (
    commands,
    parsers,
)

from .commands import *
from .parsers import *

from .append_common_args import (
    CONTEST,
    append_common_args,
)

__all__ = (
    list(commands.__all__)
    + list(parsers.__all__)
    + [
        "CONTEST",
        "append_common_args",
    ]
)
