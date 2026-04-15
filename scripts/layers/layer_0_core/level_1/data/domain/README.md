# level_1/data/domain

## Purpose
Reusable configuration dataclasses and base model components for vision and tabular domains.

## Contents
- `vision/` — `VisionConfig`, `VisionModelConfig`, `VisionDataConfig`, base model classes (`BaseVisionModel`, `BaseHead`, `RegressionHead`, `ClassificationHead`), and weight cache utilities.
- `tabular/` — `TabularConfig`, `TabularModelConfig`, `TabularDataConfig`, and `TabularDataset`.

## Public API
| Name | Description |
|------|-------------|
| `VisionConfig` | Complete config for vision tasks. |
| `VisionDataConfig` | Vision data settings (image size, augmentation, TTA). |
| `VisionModelConfig` | Vision model settings (backbone name, num_classes, dropout). |
| `BaseVisionModel` | Abstract base class all vision models must implement. |
| `BaseHead` | MLP head with configurable hidden layer, dropout, and activation. |
| `RegressionHead` | Regression-specific head. |
| `ClassificationHead` | Classification-specific head with `num_classes`. |
| `TabularConfig` | Complete config for tabular tasks. |
| `TabularDataConfig` | Tabular data settings. |
| `TabularModelConfig` | Tabular model settings. |
| `TabularDataset` | PyTorch Dataset for tabular data. |

## Dependencies
- `level_0` — `CompositeConfig`, `EvaluationSchema`, `PathConfig`, `TrainingSchema`, `get_torch`, `is_kaggle`, `get_logger`.

## Usage Example
```python
from layers.layer_0_core.level_1.data.domain import VisionConfig, TabularDataset

config = VisionConfig()
```