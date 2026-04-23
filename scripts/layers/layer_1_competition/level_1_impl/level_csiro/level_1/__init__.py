"""Auto-generated package exports."""


from .best_variant import (
    find_best_variant,
    find_variant_by_id,
    get_best_variant_info,
    get_variant_best_fold,
    load_results_json,
)

from .config_updater import (
    apply_combo_to_config,
    apply_data_combo,
)

from .e2e_ensemble_oof import generate_end_to_end_ensemble_oof_predictions_batch

from .factory import create_biomass_model

from .meta_models import (
    generate_final_predictions,
    train_meta_models,
)

from .model_selection import (
    get_top_n_variants,
    get_variant_info_from_model_id,
    load_gridsearch_metadata,
    resolve_model_paths_from_config,
    validate_model_paths,
)

from .modeling_shim import (
    csiro_modeling,
    models,
)

from .post_processor import CSIROPostProcessor

from .stacking_helpers import (
    create_and_train_stacking_ensemble,
    load_model_metadata,
    load_training_features,
)

from .train_pipeline import train_pipeline

from .variant_selection_internal import (
    find_variant_by_id,
    hyperparameters_signature,
    is_empty_list_json,
    load_and_merge_variants,
    load_gridsearch_scores,
    resolve_metadata_file_locations,
    to_jsonable,
)

__all__ = [
    "CSIROPostProcessor",
    "apply_combo_to_config",
    "apply_data_combo",
    "create_and_train_stacking_ensemble",
    "create_biomass_model",
    "csiro_modeling",
    "find_best_variant",
    "find_variant_by_id",
    "generate_end_to_end_ensemble_oof_predictions_batch",
    "generate_final_predictions",
    "get_best_variant_info",
    "get_top_n_variants",
    "get_variant_best_fold",
    "get_variant_info_from_model_id",
    "hyperparameters_signature",
    "is_empty_list_json",
    "load_and_merge_variants",
    "load_gridsearch_metadata",
    "load_gridsearch_scores",
    "load_model_metadata",
    "load_results_json",
    "load_training_features",
    "models",
    "resolve_metadata_file_locations",
    "resolve_model_paths_from_config",
    "to_jsonable",
    "train_meta_models",
    "train_pipeline",
    "validate_model_paths",
]
