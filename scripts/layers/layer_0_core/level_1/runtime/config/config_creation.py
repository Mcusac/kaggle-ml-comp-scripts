"""Config creation utilities for CLI."""
import argparse

from typing import Optional, Callable, Any

from level_0 import get_arg, ConfigValidationError


def create_config(
    contest_name: str,
    args: argparse.Namespace,
    get_contest: Callable[[str], Any],
    get_vision_config_builder: Optional[Callable[..., Any]] = None,
    get_tabular_config_builder: Optional[Callable[..., Any]] = None,
) -> Any:
    """
    Create configuration object for the contest.
    Orchestration does not import contest, vision, or tabular; caller provides
    get_contest and, per model type, get_vision_config_builder / get_tabular_config_builder.

    Args:
        contest_name: Contest name.
        args: Parsed arguments.
        get_contest: Callable that takes contest name and returns contest dict
            (paths, config, data_schema, etc.). Provided by contest layer.
        get_vision_config_builder: Optional. For model_type=='vision', callable
            (contest_name, args, data_root, output_dir, data_schema) -> config.
            Provided by scripts layer so orchestration does not import vision.
        get_tabular_config_builder: Optional. For model_type=='tabular', callable
            (contest_name, args, data_root, output_dir, data_schema) -> config.
            Provided by scripts layer so orchestration does not import tabular.

    Returns:
        Configuration object (VisionConfig or TabularConfig).
    """

    contest = get_contest(contest_name)
    contest_paths = contest['paths']()
    data_schema = contest.get('data_schema')
    
    # Detect model type from args (default: 'vision')
    model_type = get_arg(args, 'model_type', 'vision')
    
    # Get data root
    data_root = get_arg(args, 'data_root') or str(contest_paths.local_data_root)
    output_dir = get_arg(args, 'output_dir', 'output')
    
    # Create config based on model type
    if model_type == 'vision':
        if get_vision_config_builder is None:
            raise ConfigValidationError(
                "Vision config requires get_vision_config_builder from scripts layer (orchestration does not import vision)."
            )
        return get_vision_config_builder(contest_name, args, data_root, output_dir, data_schema)
    else:  # tabular
        if get_tabular_config_builder is None:
            raise ConfigValidationError(
                "Tabular config requires get_tabular_config_builder from scripts layer (orchestration does not import tabular)."
            )
        return get_tabular_config_builder(contest_name, args, data_root, output_dir, data_schema)

