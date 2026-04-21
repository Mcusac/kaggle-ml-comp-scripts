"""Auto-generated aggregation exports."""


from . import (
    parsers,
    pipelines,
    run,
    scoring,
    train,
)

from .parsers import *
from .pipelines import *
from .run import *
from .scoring import *
from .train import *

__all__ = (
    list(parsers.__all__)
    + list(pipelines.__all__)
    + list(run.__all__)
    + list(scoring.__all__)
    + list(train.__all__)
)
