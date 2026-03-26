"""Ensemble pipeline for CSIRO contest."""

import json
import pandas as pd

from pathlib import Path
from typing import Optional, List, Dict

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import get_contest

from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import regression_ensemble_pipeline

logger = get_logger(__name__)


def ensemble_pipeline(
    data_root: Optional[str] = None,
    results_files: Optional[List[str]] = None,
    top_n: int = 3,
    method: str = 'weighted_average',
    fallback_paths: Optional[List[str]] = None,
    test_filename: str = 'test.csv',
    **kwargs
) -> pd.DataFrame:
    """Ensemble top-N models from grid search results."""
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()
    data_schema = contest['data_schema']()
    post_processor = contest['post_processor']()

    if data_root is None:
        data_root = str(paths.get_data_root())

    if results_files is None:
        results_files = [str(paths.get_output_dir() / 'dataset_grid_search' / 'gridsearch_results.json')]

    all_results = []
    for results_file in results_files:
        results_path = Path(results_file)
        if results_path.exists():
            with open(results_path, 'r') as f:
                results = json.load(f)
                all_results.extend(results)

    if not all_results:
        raise ValueError("No results found in any results files")

    all_results.sort(key=lambda x: x.get('cv_score', -float('inf')), reverse=True)
    top_results = all_results[:top_n]

    logger.info(f"Ensembling top {len(top_results)} models:")
    for i, result in enumerate(top_results, 1):
        logger.info(f"  {i}. {result.get('variant_id', 'unknown')}: CV={result.get('cv_score', 0):.4f}")

    ensemble_config = {
        'method': method,
        'score_type': 'cv',
        'top_n': top_n
    }

    logger.info("Running regression ensemble pipeline...")
    submission_df = regression_ensemble_pipeline(
        data_root=data_root,
        ensemble_config=ensemble_config,
        dataset_type='split',
        test_filename=test_filename,
        batch_size=kwargs.get('batch_size', 32)
    )

    logger.info("✅ Ensemble pipeline complete!")

    return submission_df


def ensemble_pipeline_from_paths(
    data_root: Optional[str] = None,
    model_paths: Optional[List[str]] = None,
    method: str = 'weighted_average',
    submission_scores: Optional[Dict[str, float]] = None,
    score_type: str = 'cv',
    test_filename: str = 'test.csv',
    **kwargs
) -> pd.DataFrame:
    """Ensemble models from direct model paths."""
    contest = get_contest('csiro')
    paths = contest['paths']()

    if data_root is None:
        data_root = str(paths.get_data_root())

    if not model_paths:
        raise ValueError("model_paths is required for ensemble_pipeline_from_paths")

    ensemble_config = {
        'method': method,
        'score_type': score_type,
        'model_paths': model_paths,
        'submission_scores': submission_scores
    }

    logger.info(f"Ensembling {len(model_paths)} models from paths...")
    submission_df = regression_ensemble_pipeline(
        data_root=data_root,
        ensemble_config=ensemble_config,
        dataset_type='split',
        test_filename=test_filename,
        batch_size=kwargs.get('batch_size', 32)
    )

    logger.info("✅ Ensemble from paths pipeline complete!")

    return submission_df
