"""Generic test feature extraction for stacking and ensemble pipelines."""

import numpy as np

from pathlib import Path
from typing import Any, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import cleanup_gpu_memory, get_device
from layers.layer_0_core.level_2 import FeatureExtractor
from layers.layer_0_core.level_4 import load_json
from layers.layer_0_core.level_6 import create_streaming_test_dataloader

from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model

logger = get_logger(__name__)

_DEFAULT_IMAGE_SIZE: Tuple[int, int] = (224, 224)
_DEFAULT_BATCH_SIZE: int = 32


def extract_test_features_from_model(
    test_csv_path: Path | str,
    data_root: str,
    dataset_type: str,
    config: Any,
    data_schema: Any,
    feature_extraction_model_name: str = "dinov2_base",
    batch_size: int = _DEFAULT_BATCH_SIZE,
    num_workers: int = 0,
) -> np.ndarray:
    """
    Extract test features using a feature extraction model.

    Creates model, dataloader, extracts features, cleans up GPU.

    Args:
        test_csv_path: Path to test CSV
        data_root: Data root directory
        dataset_type: Dataset type (e.g. 'split', 'full')
        config: Contest config with primary_targets
        data_schema: Contest data schema with image_path_column
        feature_extraction_model_name: Model name for feature extraction
        batch_size: Batch size for dataloader
        num_workers: Dataloader workers

    Returns:
        Test features array (n_samples, n_features)
    """
    logger.info("Extracting test features...")
    device = get_device("auto")

    feature_model = create_feature_extraction_model(
        model_name=feature_extraction_model_name,
        num_primary_targets=len(config.primary_targets),
        device=device,
        image_size=None,
        pretrained=True,
    )
    feature_model.to(device)
    feature_model.eval()

    image_size = (
        feature_model.get_input_size()
        if hasattr(feature_model, "get_input_size")
        else _DEFAULT_IMAGE_SIZE
    )

    feature_extractor = FeatureExtractor(feature_model, device)
    test_loader = create_streaming_test_dataloader(
        test_csv_path=str(test_csv_path),
        data_root=data_root,
        image_path_column=data_schema.image_path_column,
        primary_targets=config.primary_targets,
        image_size=image_size,
        batch_size=batch_size,
        dataset_type=dataset_type,
        num_workers=num_workers,
    )
    test_features = feature_extractor.extract_features(
        test_loader, dataset_type=dataset_type
    )
    logger.info(f"Extracted test features shape: {test_features.shape}")

    del feature_model, feature_extractor, test_loader
    cleanup_gpu_memory()

    return test_features


def find_feature_filename_from_ensemble_metadata(
    ensemble_configs: list,
    metadata_key: str = "model_paths",
) -> str:
    """
    Find feature_filename from first model's metadata in ensemble configs.

    Args:
        ensemble_configs: List of dicts with model_paths (or metadata_key)
        metadata_key: Key in config for model paths list

    Returns:
        feature_filename from model_metadata.json

    Raises:
        ValueError: If feature_filename cannot be determined
    """
    for ensemble_config in ensemble_configs:
        model_paths = ensemble_config.get(metadata_key, [])
        if model_paths:
            first_path = model_paths[0]
            metadata_file = Path(first_path) / "model_metadata.json"
            if metadata_file.exists():
                metadata = load_json(metadata_file)
                feature_filename = metadata.get("feature_filename")
                if feature_filename:
                    return feature_filename

    raise ValueError(
        "Cannot determine feature_filename from ensemble model metadata"
    )
