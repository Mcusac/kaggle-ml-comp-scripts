# dataloader

Dataset factory and DataLoader worker initialization utilities.

## Purpose

Creates train/validation dataset pairs for DataLoader construction and provides a seeded worker initialization function for reproducible data loading.

## Contents

- `datasets.py` — `create_datasets_for_dataloaders`: factory that builds train and validation datasets from a config
- `workers.py` — `create_worker_init_fn`: returns a worker init function that seeds each DataLoader worker

## Public API

- `create_datasets_for_dataloaders(config, df_train, df_val)` — Build (train_dataset, val_dataset) from a configuration and split DataFrames
- `create_worker_init_fn(seed)` — Return a DataLoader `worker_init_fn` that seeds numpy/random/torch per worker

## Dependencies

- **level_1** — `BaseImageDataset` (dataset base class), `set_seed`

## Usage Example

```python
from torch.utils.data import DataLoader
from level_2.dataloader import create_datasets_for_dataloaders, create_worker_init_fn

train_ds, val_ds = create_datasets_for_dataloaders(config, df_train, df_val)
train_loader = DataLoader(
    train_ds,
    batch_size=32,
    worker_init_fn=create_worker_init_fn(seed=42),
    num_workers=4,
)
```
