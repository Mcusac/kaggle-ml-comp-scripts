"""Stanford RNA 3D Folding Part 2 contest implementation.

Registers `rna3d` on import so `KAGGLE_COMP_CONTEST=rna3d` resolves via the
ContestRegistry.
"""

from . import registration  # noqa: F401

from . import (
    level_0,
    level_1,
    level_2,
    level_3,
    level_4,
)

from .level_0 import *
from .level_1 import *
from .level_2 import *
from .level_3 import *
from .level_4 import *

__all__ = (
    list(level_0.__all__)
    + list(level_1.__all__)
    + list(level_2.__all__)
    + list(level_3.__all__)
    + list(level_4.__all__)
)
