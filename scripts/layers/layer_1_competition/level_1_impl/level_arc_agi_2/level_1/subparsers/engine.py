from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import get_all


def build_command(subparsers: Any) -> None:
    """
    Builds all CLI commands from the registry.
    This is the single CLI orchestration entry point.
    """

    for spec in get_all():
        parser = subparsers.add_parser(spec.name, help=spec.help)

        # Each recipe fully builds its command
        spec.builder(parser)