# datasets

## Purpose

Test data loading, dataset split caching, and dataset variant grid generation for preprocessing/augmentation.

## Contents

- **load_and_validate_test_data.py**: load_and_validate_test_data
- **prepare_test_dataframe.py**: prepare_test_dataframe_with_dummy_targets
- **splits.py**: get_dataset_cache_dir, save_dataset_splits, load_dataset_splits, apply_train_val_split
- **variants.py**: get_max_augmentation_variant, get_dataset_variant_grid

## Public API

- `load_and_validate_test_data(test_csv_path, image_path_column='image_path')` — Load test CSV, return unique images
- `prepare_test_dataframe_with_dummy_targets(unique_df, image_path_column, target_cols)` — Add zero-filled target columns
- `get_dataset_cache_dir()` — Return cache dir (Kaggle or local)
- `save_dataset_splits(train_df, val_df, cache_key, metadata=None)` — Persist splits to parquet
- `load_dataset_splits(cache_key)` — Load cached splits or None
- `apply_train_val_split(data, validation_split, random_state=42)` — Split into train/val
- `get_max_augmentation_variant()` — Return (preprocessing_options, augmentation_options)
- `get_dataset_variant_grid()` — Power set of preprocessing × augmentation combinations

## Dependencies

- level_0: ensure_dir, get_logger, is_kaggle, generate_power_set
- level_2: get_train_test_split
- level_3: validate_path_is_file
- level_4: load_csv, save_json, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION

## Usage Example

```python
from level_5 import load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets
from level_5 import save_dataset_splits, load_dataset_splits, apply_train_val_split

df = load_and_validate_test_data("test.csv")
df = prepare_test_dataframe_with_dummy_targets(df, "image_path", ["target"])

train, val = apply_train_val_split(df, 0.2)
path = save_dataset_splits(train, val, "my_variant")
cached = load_dataset_splits("my_variant")
```
