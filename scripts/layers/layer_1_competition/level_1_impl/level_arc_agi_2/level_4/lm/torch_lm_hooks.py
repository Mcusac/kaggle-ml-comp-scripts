"""Default :class:`SharedTorchLmHooks` for ARC Qwen grid chat + turbo DFS."""

from layers.layer_1_competition.level_0_infra.level_3 import SharedTorchLmHooks

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    REFERENCE_INNER_LOOP_WALL_SEC,
    arc_grid_to_text_lines,
    inference_turbo_dfs,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import ArcQwenGridChatFormatter


def arc_default_torch_lm_hooks() -> SharedTorchLmHooks:
    return SharedTorchLmHooks(
        make_formatter=lambda tokenizer: ArcQwenGridChatFormatter(tokenizer=tokenizer),
        inference_turbo_dfs=inference_turbo_dfs,
        arc_grid_to_text_lines=arc_grid_to_text_lines,
        reference_inner_loop_wall_sec=float(REFERENCE_INNER_LOOP_WALL_SEC),
    )


__all__ = ["arc_default_torch_lm_hooks"]
