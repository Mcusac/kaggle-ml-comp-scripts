from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    register,
    CommandSpec,
    add_common,
    add_model,
    add_strategy,
    add_output,
    add_max_targets,
    add_ensemble,
    add_stacking,
    add_llm,
    add_run,
)


def build_train_submit(parser):
    add_common(parser)

    parser.add_argument("--train-mode", default="end_to_end")

    add_model(parser, default="grid_cnn_v0")
    add_strategy(parser, default="single")

    add_output(parser)
    add_max_targets(parser)
    add_ensemble(parser)
    add_stacking(parser)

    add_llm(parser)
    add_run(parser)


register(CommandSpec(
    name="train_and_submit",
    help="Train then submit",
    builder=build_train_submit
))