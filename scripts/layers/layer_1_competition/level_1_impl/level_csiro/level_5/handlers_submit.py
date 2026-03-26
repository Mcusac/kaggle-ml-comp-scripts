"""Submit command handler for CSIRO CLI."""

import argparse

from layers.layer_1_competition.level_0_infra.level_1 import resolve_data_root_from_args

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import resolve_dataset_type
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import submit_lightweight_pipeline
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import get_grid_search_context


def handle_submit(args: argparse.Namespace) -> None:
    """Handle submit command."""
    ctx = get_grid_search_context()
    data_root = resolve_data_root_from_args(args)
    model_path = getattr(args, "model_path", None)
    metadata_path = getattr(args, "metadata_path", None)
    results_file = getattr(args, "results_file", None)
    model_name = getattr(args, "model_name", None)
    dataset_type = resolve_dataset_type(args)

    submit_lightweight_pipeline(
        contest_context=ctx,
        data_root=data_root,
        model_path=model_path,
        metadata_path=metadata_path,
        results_file=results_file,
        model_name=model_name,
        dataset_type=dataset_type,
    )
