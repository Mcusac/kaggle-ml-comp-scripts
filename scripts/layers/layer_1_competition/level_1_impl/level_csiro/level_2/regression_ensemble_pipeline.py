"""Regression ensemble: resolve paths, validate, extract features, ensemble predict, expand, save."""

import json
import pandas as pd

from pathlib import Path
from typing import Any, Dict

from layers.layer_0_core.level_0 import validate_predictions_shape, get_logger
from layers.layer_0_core.level_1 import get_device
from layers.layer_0_core.level_2 import FeatureExtractor
from layers.layer_0_core.level_5 import load_and_validate_test_data
from layers.layer_0_core.level_5 import save_submission_csv
from layers.layer_0_core.level_6 import create_streaming_test_dataloader
from level_8 import create_regression_ensemble_from_paths

from layers.layer_1_competition.level_0_infra.level_1 import get_contest
from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model
from layers.layer_1_competition.level_0_infra.level_5 import (
    expand_predictions_to_submission_format,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    resolve_model_paths_from_config,
    validate_model_paths,
)

_logger = get_logger(__name__)


def regression_ensemble_pipeline(
    data_root: str,
    ensemble_config: Dict[str, Any],
    dataset_type: str = 'split',
    test_filename: str = 'test.csv',
    batch_size: int = 32,
) -> pd.DataFrame:
    """
    Run regression ensemble: resolve model paths, extract features, ensemble predict, expand, save.
    """
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()
    data_schema = contest['data_schema']()
    post_processor = contest['post_processor']()

    base_model_dir = str(paths.get_models_base_dir())
    model_paths, cv_scores, _ = resolve_model_paths_from_config(
        ensemble_config,
        base_model_dir=base_model_dir,
        auto_detect=False,
    )
    validate_model_paths(model_paths, require_same_feature_model=True)

    model_configs = []
    feat_name = None
    default_model = 'dinov2_base'
    for p in model_paths:
        mf = Path(p) / 'model_metadata.json'
        if mf.exists():
            with open(mf) as f:
                model_configs.append(json.load(f))
            if feat_name is None and model_configs[-1].get('feature_filename'):
                feat_name = default_model
        else:
            model_configs.append({})
    if not feat_name:
        feat_name = default_model

    device = get_device('auto')
    ensemble = create_regression_ensemble_from_paths(
        model_paths=model_paths,
        model_configs=model_configs,
        method=ensemble_config.get('method', 'weighted_average'),
        feature_extraction_model_name=feat_name,
        cv_scores=cv_scores if ensemble_config.get('score_type') == 'cv' else None,
    )

    test_csv_path = str(Path(data_root) / test_filename)
    unique = load_and_validate_test_data(test_csv_path, image_path_column=data_schema.image_path_column)

    feat_model = create_feature_extraction_model(
        model_name=feat_name,
        num_primary_targets=config.num_primary_targets,
        device=device,
        image_size=None,
        pretrained=True,
    )
    image_size = feat_model.get_input_size()
    feat_model.to(device)
    feat_model.eval()

    loader = create_streaming_test_dataloader(
        test_csv_path=test_csv_path,
        data_root=data_root,
        image_path_column=data_schema.image_path_column,
        primary_targets=config.primary_targets,
        image_size=image_size,
        batch_size=batch_size,
        dataset_type=dataset_type,
    )
    extractor = FeatureExtractor(feat_model, device)
    features = extractor.extract_features(loader, dataset_type=dataset_type)
    _logger.info(f"Extracted features shape: {features.shape}")

    predictions = ensemble.predict(features)
    validate_predictions_shape(
        predictions,
        expected_count=len(unique),
        expected_cols=config.num_primary_targets,
    )

    submission_df = expand_predictions_to_submission_format(
        predictions,
        test_csv_path,
        contest_config=config,
        data_schema=data_schema,
        post_processor=post_processor,
    )
    out = save_submission_csv(submission_df)
    _logger.info(f"Regression ensemble done. Output: {out}")
    return submission_df
