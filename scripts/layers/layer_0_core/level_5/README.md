# level_5

## Purpose

Provides ensembling, grid search infrastructure, export pipelines, dataset helpers, model I/O, training orchestration, metadata path resolution, and shared data structures for ML competition workflows.

## Contents

| Subpackage | Description |
|------------|-------------|
| batch_loading | Batch load CSV and image files with progress |
| data_structure | Config loaders, JSON model registry, tabular base classes |
| datasets | Test data loading, split caching, variant grids |
| ensembling | Weighted combination, stacking ensemble |
| export | Model export pipeline and filesystem operations |
| file_io | Merge utilities for input + working JSON, submission CSV |
| grid_search | Checkpoint cleanup, result analysis, persistence, variant tracking |
| metadata | Metadata paths and score extraction for Kaggle/local layouts |
| model_io | Model save/load for PyTorch, sklearn, pickle |
| training | BaseModelTrainer and VisionTrainer |

## Public API

All exports are aggregated from subpackages. Import from `level_5`:

```python
from level_5 import (
    # batch_loading
    load_csv_batch,
    load_image_batch,
    # data_structure
    JSONConfigLoader,
    create_json_model_registry,
    BaseTabularModel,
    SparseTabularDataset,
    # datasets
    load_and_validate_test_data,
    prepare_test_dataframe_with_dummy_targets,
    get_dataset_cache_dir,
    save_dataset_splits,
    load_dataset_splits,
    apply_train_val_split,
    get_max_augmentation_variant,
    get_dataset_variant_grid,
    # ensembling
    apply_weighted_combination,
    combine_with_fallback,
    StackingEnsemble,
    # export
    ExportPipeline,
    find_trained_model_path,
    export_from_training_dir,
    copy_model_checkpoint,
    write_metadata_file,
    # file_io
    merge_json_from_input_and_working,
    merge_list_by_key_add_only,
    merge_list_by_key_working_replaces,
    save_submission_csv,
    # grid_search
    load_results,
    save_results,
    load_checkpoint,
    save_checkpoint,
    load_raw_results,
    extract_top_results,
    extract_parameter_ranges,
    analyze_results_for_focused_grid,
    get_focused_parameter_grid,
    cleanup_grid_search_checkpoints_retroactive,
    cleanup_checkpoints,
    load_completed_variants_helper,
    get_next_variant_index,
    save_variant_result_helper,
    # metadata
    find_project_input_root,
    find_metadata_dir,
    get_writable_metadata_dir,
    load_combo_metadata,
    extract_scores_from_json,
    resolve_best_fold_and_score,
    # model_io
    save_model_raw,
    save_model,
    load_model_raw,
    load_model,
    save_regression_model,
    # training
    BaseModelTrainer,
    VisionTrainer,
)
```

## Dependencies

- **level_0**: logging/runtime helpers, `get_torch`, errors, paths, power-set and augmentation constants where used
- **level_1**: batch loading, pipelines, weights, device/mixed precision, training checkpoints, submission paths
- **level_2**: splits, averaging, CV/regression helpers, optimizer/scheduler/loss builders, training phase executors
- **level_3**: path/file validation, regression model factory
- **level_4**: file I/O (CSV/JSON/pickle/image), vision model factory, metrics used by trainers

## Usage Example

```python
from pathlib import Path

from level_5 import load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets
from level_5 import find_metadata_dir, load_combo_metadata

df = load_and_validate_test_data(Path("test.csv"), image_path_column="image_path")
df = prepare_test_dataframe_with_dummy_targets(df, "image_path", ["target_1"])

meta = find_metadata_dir("example-metadata")
if meta:
    _ = load_combo_metadata(meta, "config.json")
```
