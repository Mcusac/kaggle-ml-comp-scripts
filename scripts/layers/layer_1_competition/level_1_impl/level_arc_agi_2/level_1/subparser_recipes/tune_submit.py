from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    register,
    CommandSpec,
    add_common,
    add_search,
    add_model,
    add_strategy,
    add_output,
    add_max_targets,
    add_ensemble,
    add_stacking,
    add_llm,
    add_run,
)


def build_tune_submit(parser):
    add_common(parser)

    add_search(parser, default="quick")

    add_model(parser, default="baseline_approx")
    add_strategy(parser, default="single")

    add_output(parser)
    add_max_targets(parser)
    add_ensemble(parser)
    add_stacking(parser)

    add_llm(parser)
    add_run(parser)


register(CommandSpec(
    name="tune_and_submit",
    help="Tune then submit",
    builder=build_tune_submit
))