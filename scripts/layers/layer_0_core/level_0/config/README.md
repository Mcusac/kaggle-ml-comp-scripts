# Config

Base configuration schemas and enums for the framework.

## Purpose

Provides root config types, runtime settings, shared dataclasses for training and evaluation schemas, pipeline settings, data split enumeration, and training modes.

## Contents

- `base_schema.py` – `BaseConfig`, `TrainingSchema`, `EvaluationSchema`, `PathConfig`, `CompositeConfig`
- `data_split.py` – `DataSplit` enum
- `extractor.py` – `get_config_value` utility
- `pipeline_config.py` – `PipelineConfig`
- `runtime_config.py` – `RuntimeConfig`
- `training_cadence.py` – `TrainingCadenceConfig`
- `training_modes.py` – `TrainingMode` enum

## Public API

- `BaseConfig` – Root type for all domain configs
- `TrainingSchema` – Schema for training hyperparameters
- `EvaluationSchema` – Schema for evaluation settings
- `PathConfig` – Output and checkpoint directory config
- `CompositeConfig` – Composes training, evaluation, and path schemas
- `get_config_value` – Safely extract a typed value from a config object
- `DataSplit` – Enum: TRAIN, VAL, TEST
- `PipelineConfig` – Grid search, CV, ensemble, and export settings
- `RuntimeConfig` – seed, device, num_workers, output_dir, log_dir, verbose, debug
- `TrainingCadenceConfig` – Log and checkpoint frequency settings
- `TrainingMode` – Enum: LOAD_OR_TRAIN, TRAIN_NEW, LOAD_ONLY

## Dependencies

stdlib only (dataclasses, pathlib, enum, typing).

## Usage Example

```python
from level_0 import BaseConfig, CompositeConfig, TrainingSchema, RuntimeConfig

runtime = RuntimeConfig(seed=0, device="cuda")
```
