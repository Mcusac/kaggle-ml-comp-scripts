"""Ensemble command handlers for CSIRO CLI."""

import argparse
import json

from layers.layer_1_competition.level_0_infra.level_1 import resolve_data_root_from_args

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import resolve_dataset_type
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import regression_ensemble_pipeline
from layers.layer_1_competition.level_1_impl.level_csiro.level_3 import (
    ensemble_pipeline,
    ensemble_pipeline_from_paths,
)



def handle_csiro_ensemble(args: argparse.Namespace) -> None:
    """Handle csiro_ensemble command."""
    data_root = resolve_data_root_from_args(args)
    model_paths = getattr(args, "model_paths", None)
    results_files = getattr(args, "results_files", None)
    top_n = getattr(args, "top_n", 3)
    method = getattr(args, "method", "weighted_average") or "weighted_average"
    fallback_paths = getattr(args, "fallback_paths", None)
    submission_scores = getattr(args, "submission_scores", None)
    score_type = getattr(args, "score_type", "cv") or "cv"
    dataset_type = resolve_dataset_type(args)

    if model_paths:
        model_paths_list = [p.strip() for p in model_paths.split(",") if p.strip()]
        submission_scores_dict = None
        if submission_scores:
            submission_scores_dict = json.loads(submission_scores)

        ensemble_pipeline_from_paths(
            data_root=data_root,
            model_paths=model_paths_list,
            method=method,
            submission_scores=submission_scores_dict,
            score_type=score_type,
            dataset_type=dataset_type,
        )
    else:
        results_files_list = None
        if results_files:
            results_files_list = [f.strip() for f in results_files.split(",") if f.strip()]
        fallback_paths_list = None
        if fallback_paths:
            fallback_paths_list = [p.strip() for p in fallback_paths.split(",") if p.strip()]

        ensemble_pipeline(
            data_root=data_root,
            results_files=results_files_list,
            top_n=top_n,
            method=method,
            fallback_paths=fallback_paths_list,
            dataset_type=dataset_type,
        )


def handle_regression_ensemble(args: argparse.Namespace) -> None:
    """Run regression ensemble pipeline from CLI args."""
    ensemble_config = json.loads(args.ensemble_config)
    data_root = resolve_data_root_from_args(args)
    dataset_type = resolve_dataset_type(args)

    regression_ensemble_pipeline(
        data_root=data_root,
        ensemble_config=ensemble_config,
        dataset_type=dataset_type,
    )
