import argparse

from layers.layer_1_competition.level_0_infra.level_1 import parse_optional_float_list


def validate_submit_args(args: argparse.Namespace) -> None:
    weights = getattr(args, "ensemble_weights", None)

    if weights and str(weights).strip():
        parse_optional_float_list(weights)
        raise ValueError(
            "ARC submit path does not use --ensemble-weights. Remove this flag."
        )