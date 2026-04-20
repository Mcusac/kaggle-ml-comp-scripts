"""Naming-alias shim around :func:`command_llm.append_llm_args`.

Kept as a focused wrapper so ``cmd_*`` builders can import a short local name
(``append_llm``) without pulling the longer infra-style name into every file.
"""

from typing import List

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import append_llm_args


def append_llm(cmd: List[str], strategy: str, **kwargs) -> None:
    append_llm_args(cmd, strategy=strategy, **kwargs)
