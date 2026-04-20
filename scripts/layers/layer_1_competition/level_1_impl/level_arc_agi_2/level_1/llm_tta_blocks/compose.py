from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    add_llm_tta_adaptation,
    add_llm_tta_augmentation,
    add_llm_tta_core,
    add_llm_tta_decoding,
    add_llm_tta_inference,
    add_llm_tta_artifacts,
    add_llm_tta_runtime,
)


def add_llm_tta_args(parser: Any) -> None:
    add_llm_tta_adaptation(parser)
    add_llm_tta_augmentation(parser)
    add_llm_tta_core(parser)
    add_llm_tta_decoding(parser)
    add_llm_tta_inference(parser)
    add_llm_tta_artifacts(parser)
    add_llm_tta_runtime(parser)
