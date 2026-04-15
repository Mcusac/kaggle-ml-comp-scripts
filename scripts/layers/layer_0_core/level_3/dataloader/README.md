# level_3 dataloader

## Purpose

DataLoader factory for creating PyTorch training and validation dataloaders from config objects or dicts.

## Contents

- `factory.py` — `create_train_dataloader` and `create_val_dataloader` public factory functions plus internal config-resolution helpers.
- `transforms.py` — `build_transforms_for_dataloaders` utility that builds paired train/val transform pipelines from `image_size` and augmentation preset.

## Public API

- `create_train_dataloader(train_data, data_root, config, image_size, ...)` — build a shuffled training DataLoader; applies the requested augmentation preset when no transform override is provided.
- `create_val_dataloader(val_data, data_root, config, image_size, ...)` — build a non-shuffled validation DataLoader; always uses preprocessing-only transforms.
- `build_transforms_for_dataloaders(image_size, augmentation, train_transform, val_transform)` — return a `(train_transform, val_transform)` tuple, respecting any pre-built overrides.

## Dependencies

- **level_0** — `get_logger`, `get_torch` for lazy PyTorch access.
- **level_1** — `StreamingDataset`, `StreamingSplitDataset` for the underlying iterable dataset implementations.
- **level_2** — `build_preprocessing_transforms`, `build_augmentation_transforms` for transform construction; `AugmentationPreset` type alias.

## Usage Example

```python
from layers.layer_0_core.level_3.dataloader import create_train_dataloader, create_val_dataloader

train_loader = create_train_dataloader(
    train_data=train_df,
    data_root="/data/images",
    config=cfg,
    image_size=(224, 224),
    augmentation="light",
)

val_loader = create_val_dataloader(
    val_data=val_df,
    data_root="/data/images",
    config=cfg,
    image_size=(224, 224),
)
```
