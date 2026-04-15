from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    register,
    CommandSpec,
    add_common,
    add_model,
    add_max_targets,
    add_run,
)


def build_train(parser):
    add_common(parser)
    add_model(parser, default="baseline_approx")
    add_max_targets(parser, default=0)
    add_run(parser)


register(CommandSpec(
    name="train",
    help="Train ARC models",
    builder=build_train
))