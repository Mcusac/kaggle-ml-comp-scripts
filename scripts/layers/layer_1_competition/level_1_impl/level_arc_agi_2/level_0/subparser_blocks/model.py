from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import add_models_arg


def add_model(parser: Any, default: str, help_text: str | None = None) -> None:
    """
    Model selection for ARC pipeline (heuristic or neural).
    """
    add_models_arg(parser, default=default, help_text=help_text)