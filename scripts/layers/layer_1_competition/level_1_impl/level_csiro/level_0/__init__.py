"""Auto-generated package exports."""


from .aggregate import aggregate_train_csv

from .biomass_models import (
    BiomassCatBoostModel,
    BiomassGBModel,
    BiomassHistGBModel,
    BiomassLGBMModel,
    BiomassRidgeModel,
    BiomassXGBModel,
)

from .biomass_semantic_features import (
    BIOMASS_CONCEPT_GROUPS,
    BiomassSemanticFeatureExtractor,
    generate_biomass_semantic_features,
)

from .camera_trap import (
    BOTTOM_ARTIFACT_RATIO,
    ORANGE_LOWER,
    ORANGE_UPPER,
    clean_camera_trap_batch,
    clean_camera_trap_image,
)

from .checkpoint_utils import load_model_from_checkpoint

from .config import CSIROConfig

from .config_helper import ContestConfigHelper

from .config_setup import setup_contest_config

from .constants import (
    CSIRO_REGRESSION_MODEL_TYPES,
    validate_regression_model_type,
)

from .csiro_ensemble import (
    CSIROPerTargetWeightedEnsemble,
    CSIROTargetSpecificEnsemble,
    CSIRO_TARGET_NAMES,
)

from .csiro_grid_search_base import CSIROGridSearchBase

from .csiro_metadata import (
    CSIRO_COMBO_SUBPATH,
    CSIRO_DATASET_NAME,
    extract_preprocessing_augmentation_from_variant,
    find_metadata_dir,
    get_writable_metadata_dir,
    load_combo_metadata,
)

from .data_schema import CSIRODataSchema

from .derived_targets import (
    NUM_PRIMARY_TARGETS,
    compute_derived_targets,
)

from .export_ops import (
    export_trained_model,
    handle_export_only_mode,
)

from .handlers_common import (
    CSIRO_COMMANDS,
    add_common_args,
    resolve_dataset_type,
)

from .metrics import (
    CSIROWeightedR2Metric,
    DEFAULT_TARGET_ORDER,
    DEFAULT_TARGET_WEIGHTS,
    NUM_PRIMARY_TARGETS,
    NUM_TOTAL_TARGETS,
    calc_metric,
    calculate_csiro_metric,
    calculate_weighted_r2,
)

from .model_constants import MODEL_ID_MAP

from .model_resolution import (
    get_model_id_from_name,
    get_model_image_size_for_extraction,
    resolve_feature_filename,
)

from .notebook_commands import build_run_py_command

from .oom_handlers import handle_oom_error_with_retry

from .paths import CSIROPaths

from .stacking_utils import (
    load_and_run_model_inference,
    process_fold_predictions,
    process_single_fold_for_e2e_ensemble,
)

from .variants import csiro_dataset_grid

__all__ = [
    "BIOMASS_CONCEPT_GROUPS",
    "BOTTOM_ARTIFACT_RATIO",
    "BiomassCatBoostModel",
    "BiomassGBModel",
    "BiomassHistGBModel",
    "BiomassLGBMModel",
    "BiomassRidgeModel",
    "BiomassSemanticFeatureExtractor",
    "BiomassXGBModel",
    "CSIROConfig",
    "CSIRODataSchema",
    "CSIROGridSearchBase",
    "CSIROPaths",
    "CSIROPerTargetWeightedEnsemble",
    "CSIROTargetSpecificEnsemble",
    "CSIROWeightedR2Metric",
    "CSIRO_COMBO_SUBPATH",
    "CSIRO_COMMANDS",
    "CSIRO_DATASET_NAME",
    "CSIRO_REGRESSION_MODEL_TYPES",
    "CSIRO_TARGET_NAMES",
    "ContestConfigHelper",
    "DEFAULT_TARGET_ORDER",
    "DEFAULT_TARGET_WEIGHTS",
    "MODEL_ID_MAP",
    "NUM_PRIMARY_TARGETS",
    "NUM_TOTAL_TARGETS",
    "ORANGE_LOWER",
    "ORANGE_UPPER",
    "add_common_args",
    "aggregate_train_csv",
    "build_run_py_command",
    "calc_metric",
    "calculate_csiro_metric",
    "calculate_weighted_r2",
    "clean_camera_trap_batch",
    "clean_camera_trap_image",
    "compute_derived_targets",
    "csiro_dataset_grid",
    "export_trained_model",
    "extract_preprocessing_augmentation_from_variant",
    "find_metadata_dir",
    "generate_biomass_semantic_features",
    "get_model_id_from_name",
    "get_model_image_size_for_extraction",
    "get_writable_metadata_dir",
    "handle_export_only_mode",
    "handle_oom_error_with_retry",
    "load_and_run_model_inference",
    "load_combo_metadata",
    "load_model_from_checkpoint",
    "process_fold_predictions",
    "process_single_fold_for_e2e_ensemble",
    "resolve_dataset_type",
    "resolve_feature_filename",
    "setup_contest_config",
    "validate_regression_model_type",
]
