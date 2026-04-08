"""Contest protocols (on-disk: ``infra/level_0/abstractions``; import via ``layers.layer_1_competition.level_0_infra.level_0``)."""

from .contest_abstractions import (
    ContestInputValidator,
    ContestMetric,
    ContestPipelineProtocol,
)
from .run_paths_protocol import ContestRunPathsProtocol

from layers.layer_0_core.level_0 import PipelineResult

__all__ = [
    "ContestInputValidator",
    "ContestMetric",
    "ContestPipelineProtocol",
    "ContestRunPathsProtocol",
    "PipelineResult",
]
