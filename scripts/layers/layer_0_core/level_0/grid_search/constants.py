"""Constants for grid search pipelines."""

# Grid search type identifiers
GRID_SEARCH_TYPE_DATASET = 'dataset_grid_search'
GRID_SEARCH_TYPE_HYPERPARAMETER = 'hyperparameter_grid_search'

# Hyperparameter search types
SEARCH_TYPE_DEFAULTS = 'defaults'
SEARCH_TYPE_QUICK = 'quick'
SEARCH_TYPE_IN_DEPTH = 'in_depth'
SEARCH_TYPE_THOROUGH = 'thorough'
SEARCH_TYPE_FOCUSED_IN_DEPTH = 'focused_in_depth'
SEARCH_TYPE_FOCUSED_THOROUGH = 'focused_thorough'

# Valid hyperparameter search types
VALID_HYPERPARAMETER_SEARCH_TYPES = {
    SEARCH_TYPE_DEFAULTS,
    SEARCH_TYPE_QUICK,
    SEARCH_TYPE_IN_DEPTH,
    SEARCH_TYPE_THOROUGH,
    SEARCH_TYPE_FOCUSED_IN_DEPTH,
    SEARCH_TYPE_FOCUSED_THOROUGH
}

# Focused search types (require previous_results_file)
FOCUSED_SEARCH_TYPES = {
    SEARCH_TYPE_FOCUSED_IN_DEPTH,
    SEARCH_TYPE_FOCUSED_THOROUGH
}

# Dataset types
DATASET_TYPE_FULL = 'full'
DATASET_TYPE_SPLIT = 'split'

# Results file names (unified format)
RESULTS_FILE_GRIDSEARCH = 'gridsearch_results.json'

# Grid search type field values (for unified results format)
GRID_SEARCH_TYPE_FIELD_DATASET = 'dataset'
GRID_SEARCH_TYPE_FIELD_HYPERPARAMETER = 'hyperparameter'

# Best variant file names
BEST_VARIANT_FILE_DATASET = 'best_dataset_variant.json'
BEST_HYPERPARAMETERS_FILE = 'best_hyperparameters.json'

# Model directory names
MODEL_DIR_DATASET_GRID_SEARCH = 'dataset_grid_search'
MODEL_DIR_HYPERPARAMETER_GRID_SEARCH = 'hyperparameter_grid_search'

# Cleanup constants
DEFAULT_KEEP_TOP_VARIANTS = 20
DEFAULT_CLEANUP_INTERVAL = 10