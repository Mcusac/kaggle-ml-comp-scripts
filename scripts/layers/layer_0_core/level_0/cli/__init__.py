"""CLI argument parsing and command dispatch."""

from .args_utils import (
    get_arg, parse_comma_separated, 
    comma_separated_type, parse_key_value_pairs
    )
from .argument_groups import (
    add_model_type_argument,
    add_model_path_argument,
    add_ensemble_method_argument,
)
from .commands import Command
from .common_args import add_common_arguments
from .dispatcher import dispatch_command

__all__ = [
    "get_arg",
    "parse_comma_separated",
    "comma_separated_type",
    "parse_key_value_pairs",
    "add_model_type_argument",
    "add_model_path_argument",
    "add_ensemble_method_argument",
    "Command",
    "add_common_arguments",
    "dispatch_command",
]
