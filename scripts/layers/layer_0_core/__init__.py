"""Layer 0: Core utilities (general stack).

Re-exports symbols from ``level_0`` through ``level_10`` for
``from layers.layer_0_core import ...``. For new code, prefer importing from
``layers.layer_0_core.level_K`` (or the top-level ``level_K`` package when using
path bootstrap) so dependencies stay explicit.
"""

from . import (
    level_0,
    level_1,
    level_2,
    level_3,
    level_4,
    level_5,
    level_6,
    level_7,
    level_8,
    level_9,
    level_10,
)

from .level_0 import *
from .level_1 import *
from .level_2 import *
from .level_3 import *
from .level_4 import *
from .level_5 import *
from .level_6 import *
from .level_7 import *
from .level_8 import *
from .level_9 import *
from .level_10 import *

__all__ = (
    list(level_0.__all__)
    + list(level_1.__all__)
    + list(level_2.__all__)
    + list(level_3.__all__)
    + list(level_4.__all__)
    + list(level_5.__all__)
    + list(level_6.__all__)
    + list(level_7.__all__)
    + list(level_8.__all__)
    + list(level_9.__all__)
    + list(level_10.__all__)
)