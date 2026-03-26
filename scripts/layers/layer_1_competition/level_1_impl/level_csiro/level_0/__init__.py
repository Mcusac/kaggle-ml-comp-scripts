"""CSIRO level_0 package. Aggregates symbols from modules within this package."""

from .aggregate import aggregate_train_csv
from .constants import validate_regression_model_type
from .biomass_semantic_features import (
    BiomassSemanticFeatureExtractor,
    generate_biomass_semantic_features,
)
from .camera_trap import clean_camera_trap_batch, clean_camera_trap_image
from .biomass_models import (
    BiomassCatBoostModel,
    BiomassGBModel,
    BiomassHistGBModel,
    BiomassLGBMModel,
    BiomassRidgeModel,
    BiomassXGBModel,
)
from .checkpoint_utils import load_model_from_checkpoint
from .config import CSIROConfig
from .config_setup import setup_contest_config
from .csiro_metadata import (
    extract_preprocessing_augmentation_from_variant,
    find_metadata_dir,
    get_writable_metadata_dir,
    load_combo_metadata,
)
from .export_ops import export_trained_model, handle_export_only_mode
from .handlers_common import CSIRO_COMMANDS, add_common_args, resolve_dataset_type
from .metrics import calc_metric
from .model_resolution import get_model_image_size_for_extraction, resolve_feature_filename
from .stacking_utils import process_single_fold_for_e2e_ensemble

__all__ = [
    "BiomassSemanticFeatureExtractor",
    "generate_biomass_semantic_features",
    "clean_camera_trap_batch",
    "clean_camera_trap_image",
    "BiomassCatBoostModel",
    "BiomassGBModel",
    "BiomassHistGBModel",
    "BiomassLGBMModel",
    "BiomassRidgeModel",
    "BiomassXGBModel",
    "CSIRO_COMMANDS",
    "CSIROConfig",
    "add_common_args",
    "aggregate_train_csv",
    "calc_metric",
    "export_trained_model",
    "extract_preprocessing_augmentation_from_variant",
    "find_metadata_dir",
    "get_model_image_size_for_extraction",
    "get_writable_metadata_dir",
    "handle_export_only_mode",
    "load_combo_metadata",
    "load_model_from_checkpoint",
    "process_single_fold_for_e2e_ensemble",
    "resolve_dataset_type",
    "resolve_feature_filename",
    "setup_contest_config",
    "validate_regression_model_type",
]
