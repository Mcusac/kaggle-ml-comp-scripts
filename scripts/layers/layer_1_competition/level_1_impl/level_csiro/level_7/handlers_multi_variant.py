"""Multi-variant regression training command handler for CSIRO CLI."""

import argparse

from layers.layer_1_competition.level_0_infra.level_1 import resolve_data_root_from_args
from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import resolve_dataset_type

from .multi_variant_regression_training_pipeline import (
    multi_variant_regression_training_pipeline,
)


def handle_multi_variant_regression_train(args: argparse.Namespace) -> None:
    """Handle multi_variant_regression_train command."""
    data_root = resolve_data_root_from_args(args)
    feature_extraction_model = getattr(args, "feature_extraction_model")
    regression_model_type = getattr(args, "regression_model_type")
    model_ids_str = getattr(args, "model_ids")
    model_ids = [mid.strip() for mid in model_ids_str.split(",") if mid.strip()]
    extract_features = getattr(args, "extract_features", True)
    data_manipulation_combo = getattr(args, "data_manipulation_combo", None)
    fresh_train = getattr(args, "fresh_train", False)
    dataset_type = resolve_dataset_type(args)

    multi_variant_regression_training_pipeline(
        data_root=data_root,
        model_ids=model_ids,
        feature_extraction_model=feature_extraction_model,
        regression_model_type=regression_model_type,
        data_manipulation_combo=data_manipulation_combo,
        extract_features=extract_features,
        fresh_train=fresh_train,
        dataset_type=dataset_type,
    )
