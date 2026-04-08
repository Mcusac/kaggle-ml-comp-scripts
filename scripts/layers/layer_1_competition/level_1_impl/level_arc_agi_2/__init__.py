"""ARC-AGI-2 contest implementation package."""

from . import registration  # noqa: F401

from . import level_0, level_1, level_2, level_3, level_4, level_5, level_6, level_7

from .level_0 import *
from .level_1 import *
from .level_2 import *
from .level_3 import *
from .level_4 import *
from .level_5 import *
from .level_6 import *
from .level_7 import *

__all__ = (
    list(level_0.__all__)
    + list(level_1.__all__)
    + list(level_2.__all__)
    + list(level_3.__all__)
    + list(level_4.__all__)
    + list(level_5.__all__)
    + list(level_6.__all__)
    + list(level_7.__all__)
)