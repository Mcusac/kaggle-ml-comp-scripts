from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_core
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_augmentation
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_decoding
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_adaptation
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_runtime
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_inference
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_artifacts


def add_llm_tta_args(parser: Any) -> None:
    add_llm_tta_core(parser)
    add_llm_tta_augmentation(parser)
    add_llm_tta_decoding(parser)
    add_llm_tta_adaptation(parser)
    add_llm_tta_runtime(parser)
    add_llm_tta_inference(parser)
    add_llm_tta_artifacts(parser)