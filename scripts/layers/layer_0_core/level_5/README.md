# level_5

## Purpose

Provides ensembling, grid search infrastructure, export pipelines, datasets, metrics, model I/O, training orchestration, and data structures for ML competition workflows.

## Contents

| Subpackage | Description |
|------------|-------------|
| batch_loading | Batch load CSV and image files with progress |
| data_structure | Config loaders, JSON model registry, tabular base classes |
| datasets | Test data loading, splits, variant grids |
| ensembling | Weighted combination, stacking ensemble |
| export | Model export pipeline and operations |
| file_io | Merge utilities for input + working JSON |
| grid_search | Checkpoint cleanup, result analysis, persistence, variant tracking |
| metadata | Metadata path resolution for Kaggle/local |
| metrics | Unified metric calculation by task type |
| model_io | Model save/load for PyTorch, sklearn, pickle |
| training | BaseModelTrainer for vision models |

## Public API

All exports are aggregated from subpackages. Import from `level_5`:

```python
from level_5 import (
    load_csv_batch,
    load_image_batch,
    JSONConfigLoader,
    create_json_model_registry,
    BaseTabularModel,
    SparseTabularDataset,
    load_and_validate_test_data,
    prepare_test_dataframe_with_dummy_targets,
    get_dataset_cache_dir,
    save_dataset_splits,
    load_dataset_splits,
    apply_train_val_split,
    get_max_augmentation_variant,
    get_dataset_variant_grid,
    apply_weighted_combination,
    combine_with_fallback,
    StackingEnsemble,
    ExportPipeline,
    find_trained_model_path,
    export_from_training_dir,
    copy_model_checkpoint,
    write_metadata_file,
    cleanup_grid_search_checkpoints_retroactive,
    cleanup_checkpoints,
    load_raw_results,
    extract_top_results,
    extract_parameter_ranges,
    analyze_results_for_focused_grid,
    load_results,
    save_results,
    load_checkpoint,
    save_checkpoint,
    load_completed_variants_helper,
    get_next_variant_index,
    save_variant_result_helper,
    find_metadata_dir,
    get_writable_metadata_dir,
    load_combo_metadata,
    calculate_metrics,
    calculate_metric_by_name,
    save_model_raw,
    save_model,
    load_model_raw,
    load_model,
    save_regression_model,
    BaseModelTrainer,
    merge_json_from_input_and_working,
    merge_list_by_key_add_only,
    merge_list_by_key_working_replaces,
)
```

## Dependencies

- **level_0**: get_logger, ensure_dir, ensure_file_dir, is_kaggle, generate_power_set, get_torch, is_torch_available, ModelError, ModelLoadError
- **level_1**: load_batch, ensure_positive_weights, normalize_weights, BasePipeline, validate_config_section_exists, get_device, extract_config_settings, get_training_config_value, setup_mixed_precision, get_metric, list_metrics
- **level_2**: get_train_test_split, simple_average, get_ridge, get_kfold, create_optimizer, create_scheduler, create_loss_function, finalize_epoch, TrainingPhaseHelper, ValidationPhaseHelper, ModelCheckpointer
- **level_3**: validate_path_is_file, validate_file_exists, create_regression_model
- **level_4**: load_image, load_csv, load_json, save_json, save_pickle, load_pickle, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION, calculate_classification_metrics, calculate_regression_metrics, create_vision_model

## Usage Example

```python
from level_5 import load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets
from level_5 import calculate_metrics, BaseModelTrainer

# Load test data
df = load_and_validate_test_data("test.csv", image_path_column="image_path")
df = prepare_test_dataframe_with_dummy_targets(df, "image_path", ["target_1", "target_2"])

# Calculate regression metrics
metrics = calculate_metrics("regression", y_true, y_pred, target_names=["h1", "h2"])

# Train vision model
trainer = BaseModelTrainer(config, model_name="resnet50")
history = trainer.train(train_loader, val_loader, save_dir="output/models")
```
