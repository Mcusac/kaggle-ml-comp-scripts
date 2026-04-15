
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


def build_submit(parser):
    add_common(parser)

    add_strategy(parser, default="single")
    add_model(parser, default="baseline_approx")

    parser.add_argument("--train-mode", default="end_to_end")

    add_output(parser)
    add_max_targets(parser)
    add_ensemble(parser)
    add_stacking(parser)

    parser.add_argument("--tuned-config", type=str, default=None)
    parser.add_argument("--neural-checkpoint", type=str, default=None)
    parser.add_argument("--neural-train-config", type=str, default=None)

    add_llm(parser)
    add_run(parser)


register(CommandSpec(
    name="submit",
    help="Generate submission",
    builder=build_submit
))