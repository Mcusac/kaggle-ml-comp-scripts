import argparse


def validate_stacking_args(args: argparse.Namespace) -> None:
    if getattr(args, "use_validation_for_stacking", True) is False:
        raise ValueError(
            "ARC does not support stacking strategies; --no-validation-stacking is not applicable."
        )