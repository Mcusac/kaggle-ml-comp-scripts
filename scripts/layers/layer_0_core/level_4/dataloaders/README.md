# level_4.dataloaders

## Purpose

Creates PyTorch DataLoaders from DataFrames for vision training and inference. Wraps level_2 dataloader and level_3 transforms.

## Contents

| Module | Description |
|--------|-------------|
| create_dataloaders | Create train and validation DataLoaders |
| create_test_dataloader | Create test DataLoader |

## Public API

| Export | Description |
|--------|-------------|
| create_dataloaders | Create train and validation DataLoaders |
| create_test_dataloader | Create test DataLoader |

## Dependencies

- **level_0** — get_logger
- **level_2** — build_preprocessing_transforms, create_dataloader_from_dataset, create_dataset_for_test_dataloader, create_datasets_for_dataloaders, create_worker_init_fn, validate_dataframe
- **level_3** — build_transforms_for_dataloaders

## Usage Example

```python
from level_4 import create_dataloaders, create_test_dataloader

train_loader, val_loader = create_dataloaders(
    train_df, val_df, image_dir="/path/to/images",
    target_cols=["target1", "target2"], batch_size=64
)
test_loader = create_test_dataloader(test_df, image_dir="/path/to/images")
```
