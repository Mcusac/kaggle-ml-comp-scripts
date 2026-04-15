from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    register,
    CommandSpec,
    add_common,
    add_search,
    add_max_targets,
    add_run,
)


def build_tune(parser):
    add_common(parser)

    add_search(parser, default="quick")
    add_max_targets(parser)
    add_run(parser)


register(CommandSpec(
    name="tune",
    help="Tune ARC heuristic",
    builder=build_tune
))