"""Register the `cafa` contest with ContestRegistry on package import."""

from layers.layer_1_competition.level_0_infra.level_1.registry import register_contest

from .level_0.config import CAFAConfig
from .level_0.data_schema import CAFADataSchema
from .level_0.paths import CAFAPaths
from .level_1.post_processor import CAFAPostProcessor

register_contest(
    "cafa",
    CAFAConfig,
    CAFADataSchema,
    CAFAPaths,
    CAFAPostProcessor,
)
