---
generated: 2026-04-08
audit_scope: general
level_name: level_1
pass_number: 1
artifact_kind: inventory
audit_profile: full
run_id: general-stack-orchestrator-2026-04-08
---

# INVENTORY: level_1

## 1. Package & File Tree

(Excludes `__pycache__` and `.pyc`.)

```
level_1/
__init__.py
cli/
  __init__.py
  builders/
    __init__.py
    ensemble/
      __init__.py
      builder.py
      weights.py
    grid_search.py
    regression_ensemble.py
    stacking.py
    submission.py
    train_export.py
  README.md
  subparsers.py
data/
  __init__.py
  cv_splits/
    __init__.py
    arrays.py
    dataframes.py
    README.md
  domain/
    __init__.py
    README.md
    tabular/
      __init__.py
      config.py
      tabular_dataset.py
    vision/
      __init__.py
      config.py
      models/
        __init__.py
        base.py
        base_head.py
        weight_cache.py
  io/
    __init__.py
    batch_loading.py
    numpy_loader.py
    README.md
  processing/
    __init__.py
    augmentation/
      __init__.py
      blur.py
      color.py
      geometric.py
      noise.py
      pipeline.py
      README.md
    datasets/
      __init__.py
      image_datasets.py
      README.md
      streaming_datasets.py
    preprocessing/
      __init__.py
      contrast_enhancement.py
      image_base.py
      normalization.py
      README.md
      resizing.py
    README.md
  README.md
evaluation/
  __init__.py
  loss_types.py
  metric_registry.py
  README.md
  results_analysis.py
features/
  __init__.py
  base_feature_extractor.py
  cache/
    __init__.py
    config.py
    filename.py
    README.md
  feature_registry.py
  film.py
  fuse_embeddings.py
  physicochemical_features.py
  README.md
  siglip_classes.py
grid_search/
  __init__.py
  pareto_frontier.py
guards/
  __init__.py
  arrays.py
  collections.py
  config.py
  ensembles.py
  none.py
  README.md
  result_checks.py
io/
  __init__.py
  README.md
  tsv_submission_formatter.py
ontology/
  __init__.py
  config_resolver.py
  hierarchy_propagator.py
  README.md
pipelines/
  __init__.py
  orchestration.py
  pipeline_shells.py
protein/
  __init__.py
  id_utils.py
  README.md
README.md
runtime/
  __init__.py
  base_pipeline.py
  chunked_prediction.py
  config/
    __init__.py
    config_creation.py
    config_sections.py
    evaluation.py
    grid_search.py
    README.md
    training.py
  cuda/
    __init__.py
    gpu_cleanup.py
    memory.py
    monitoring.py
    README.md
  device.py
  lazy_imports.py
  metadata_paths.py
  notebook_runner.py
  paths.py
  process.py
  progress_config.py
  README.md
  seed.py
search/
  __init__.py
  profiles/
    __init__.py
    README.md
    regression.py
    search_type_utils.py
    training.py
    transformer.py
    vision.py
  README.md
  variants/
    __init__.py
    augmentation_variants.py
    execution_logging.py
    executor.py
    param_grid.py
    README.md
    scoring.py
training/
  __init__.py
  batch_processor.py
  checkpoint.py
  epochs/
    __init__.py
    executor.py
    logging.py
  forward_pass.py
  model_io.py
  README.md
  setup.py
```

## 2. Per-File Details

### FILE: level_1/__init__.py
  Module docstring: Level 1: Framework utilities. Depends only on level_0.
  Imports:
    - from . import cli, data, evaluation, features, grid_search, guards, io, ontology, pipelines, protein, runtime, search, training
    - from .cli import *
    - from .data import *
    - from .evaluation import *
    - from .features import *
    - from .grid_search import *
    - from .guards import *
    - from .io import *
    - from .ontology import *
    - from .pipelines import *
    - from .protein import *
    - from .runtime import *
    - from .search import *
    - from .training import *
  Line count: 33

### FILE: level_1/cli/__init__.py
  Module docstring: CLI package: command-line interface utilities.
  Imports:
    - from . import builders
    - from .builders import *
    - from .subparsers import setup_framework_subparsers
  Line count: 12

### FILE: level_1/cli/builders/__init__.py
  Module docstring: CLI command builders for subprocess construction.
  Imports:
    - from . import ensemble
    - from .ensemble import *
    - from .grid_search import GridSearchCommandBuilder
    - from .regression_ensemble import RegressionEnsembleCommandBuilder
    - from .stacking import StackingCommandBuilder
    - from .submission import SubmissionCommandBuilder
    - from .train_export import TrainExportCommandBuilder
  Line count: 19

### FILE: level_1/cli/builders/ensemble/__init__.py
  Module docstring: Command builder factory utilities.
  Imports:
    - from .builder import EnsembleCommandBuilder
    - from .weights import ensure_positive_weights, normalize_weights
  Line count: 13
  __all__: ['EnsembleCommandBuilder', 'ensure_positive_weights', 'normalize_weights']

### FILE: level_1/cli/builders/ensemble/builder.py
  Module docstring: Command builder for ensemble execution.
  Classes:
    - EnsembleCommandBuilder
        Methods:
                 def __init__(self, contest: str, models: List[str], method: Optional[str]=None): super().__init__() self.add_positional('ensemble') self.add_option('--contest', contest) self.add_list_option('--model', models) self.add_option('--method', method)
  Imports:
    - from typing import List, Optional
    - from level_0 import BaseCommandBuilder [internal level_0]
  Line count: 23

### FILE: level_1/cli/builders/ensemble/weights.py
  Module docstring: Weight manipulation helpers for ensemble methods.
  Functions:
    - def ensure_positive_weights(weights_array: np.ndarray) -> np.ndarray: """Ensure all weights are positive and non-zero.""" weights = weights_array.copy() min_weight = np.min(weights) if min_weight <= 0: weights = weights - min_weight + EPSILON_WEIGHT return np.maximum(weights, EPSILON_WEIGHT)
    - def normalize_weights(weights_array: np.ndarray) -> np.ndarray: """Normalize weights to sum to 1.0. Args: weights_array: Array of weights. Returns: Weights normalised to sum to 1.0. Raises: DataValidationError: If weights sum to zero. """ weight_sum = np.sum(weights_array) if np.isclose(weight_sum, 0.0): raise DataValidationError('Weights sum to zero; cannot normalise.') return weights_array / weight_sum
  Imports:
    - import numpy as np
    - from layers.layer_0_core.level_0 import DataValidationError [internal level_0]
  Line count: 34

### FILE: level_1/cli/builders/grid_search.py
  Module docstring: Command builder for grid search execution.
  Classes:
    - GridSearchCommandBuilder
        Methods:
                 def __init__(self, contest: str, config: str, search_type: Optional[str]=None, fold: Optional[int]=None): super().__init__() self.add_positional('grid_search') self.add_option('--contest', contest) self.add_option('--config', config) self.add_option('--search-type', search_type) self.add_option('--fold', fold)
  Imports:
    - from typing import Optional
    - from layers.layer_0_core.level_0 import BaseCommandBuilder [internal level_0]
  Line count: 25

### FILE: level_1/cli/builders/regression_ensemble.py
  Module docstring: Command builder for regression ensemble execution.
  Classes:
    - RegressionEnsembleCommandBuilder
        Methods:
                 def __init__(self, contest: str, models: List[str]): super().__init__() self.add_positional('regression_ensemble') self.add_option('--contest', contest) self.add_list_option('--model', models)
  Imports:
    - from typing import List
    - from layers.layer_0_core.level_0 import BaseCommandBuilder [internal level_0]
  Line count: 21

### FILE: level_1/cli/builders/stacking.py
  Module docstring: Command builder for stacking execution.
  Classes:
    - StackingCommandBuilder
        Methods:
                 def __init__(self, contest: str, base_models: List[str], meta_model: str): super().__init__() self.add_positional('stacking') self.add_option('--contest', contest) self.add_list_option('--base-model', base_models) self.add_option('--meta-model', meta_model)
  Imports:
    - from typing import List
    - from layers.layer_0_core.level_0 import BaseCommandBuilder [internal level_0]
  Line count: 23

### FILE: level_1/cli/builders/submission.py
  Module docstring: Command builder for submission generation.
  Classes:
    - SubmissionCommandBuilder
        Methods:
                 def __init__(self, contest: str, model: str, tta: bool=False, output: Optional[str]=None): super().__init__() self.add_positional('submit') self.add_option('--contest', contest) self.add_option('--model', model) self.add_flag('--tta', tta) self.add_option('--output', output)
  Imports:
    - from typing import Optional
    - from layers.layer_0_core.level_0 import BaseCommandBuilder [internal level_0]
  Line count: 25

### FILE: level_1/cli/builders/train_export.py
  Module docstring: Command builder for train/export execution.
  Classes:
    - TrainExportCommandBuilder
        Methods:
                 def __init__(self, contest: str, config: str, fold: Optional[int]=None, export: bool=False, device: Optional[str]=None): super().__init__() self.add_positional('train_export') self.add_option('--contest', contest) self.add_option('--config', config) self.add_option('--fold', fold) self.add_option('--device', device) self.add_flag('--export', export)
  Imports:
    - from typing import Optional
    - from layers.layer_0_core.level_0 import BaseCommandBuilder [internal level_0]
  Line count: 27

### FILE: level_1/cli/subparsers.py
  Module docstring: Framework CLI builders.
  Functions:
    - def setup_framework_subparsers(subparsers: argparse._SubParsersAction, model_type_choices: Sequence[str], ensemble_methods: Sequence[str], skip_commands: Optional[AbstractSet[str]]=None) -> None: """ Define all framework-level CLI commands. This function only defines CLI structure. It does not contain business logic. Args: skip_commands: Subcommand names to omit so contest handlers can register the same name without argparse conflicts (e.g. train, submit). """ skip = skip_commands or frozenset() if 'train' not in skip: train = subparsers.add_parser('train', help='Train a model') add_common_arguments(train) train.add_argument('--batch-size', type=int, help='Batch size') train.add_argument('--lr', type=float, help='Learning rate') add_model_type_argument(train, model_type_choices) test = subparsers.add_parser('test', help='Test/Predict with trained model') add_common_arguments(test) add_model_path_argument(test, required=True) add_model_type_argument(test, model_type_choices) test.add_argument('--use-tta', action='store_true', help='Use test-time augmentation') train_test = subparsers.add_parser('train_test', help='Train and test') add_common_arguments(train_test) add_model_type_argument(train_test, model_type_choices) grid = subparsers.add_parser('grid_search', help='Run hyperparameter search') add_common_arguments(grid) grid.add_argument('--search-type', choices=['quick', 'in_depth'], default='quick', help='Grid search type') add_model_type_argument(grid, model_type_choices) cv = subparsers.add_parser('cross_validate', help='Run k-fold cross-validation') add_common_arguments(cv) cv.add_argument('--n-folds', type=int, default=5, help='Number of folds') add_model_type_argument(cv, model_type_choices) ensemble = subparsers.add_parser('ensemble', help='Generate ensemble predictions') add_common_arguments(ensemble) ensemble.add_argument('--model-paths', type=str, required=True, help='Comma-separated model paths') add_ensemble_method_argument(ensemble, ensemble_methods) ensemble.add_argument('--weights', type=str, help='Comma-separated weights') export = subparsers.add_parser('export', help='Export trained model') add_common_arguments(export) add_model_path_argument(export, required=True) export.add_argument('--export-dir', type=str, required=True, help='Export directory') if 'submit' not in skip: submit = subparsers.add_parser('submit', help='Submit predictions') add_common_arguments(submit) add_model_path_argument(submit) submit.add_argument('--strategy', choices=['single', 'ensemble', 'stacking', 'stacking_ensemble'], default='single', help='Submission strategy') submit.add_argument('--models', type=str, help='Comma-separated model names') submit.add_argument('--ensemble-weights', type=str, help='Comma-separated weights') submit.add_argument('--use-validation-for-stacking', action='store_true') submit.add_argument('--max-targets', type=int) submit.add_argument('--output-csv', type=str)
  Imports:
    - import argparse
    - from typing import AbstractSet, Optional, Sequence
    - from level_0 import add_common_arguments, add_model_type_argument, add_model_path_argument, add_ensemble_method_argument [internal level_0]
  Line count: 114

### FILE: level_1/data/__init__.py
  Module docstring: Data package: image processing utilities and domain data structures.
  Imports:
    - from . import cv_splits, domain, io, processing
    - from .cv_splits import *
    - from .domain import *
    - from .io import *
    - from .processing import *
  Line count: 16

### FILE: level_1/data/cv_splits/__init__.py
  Module docstring: Cross-validation split utilities: arrays and DataFrames.
  Imports:
    - from .arrays import split_features_by_fold
    - from .dataframes import create_kfold_splits, get_fold_data
  Line count: 10
  __all__: ['split_features_by_fold', 'create_kfold_splits', 'get_fold_data']

### FILE: level_1/data/cv_splits/arrays.py
  Module docstring: Split features and targets by fold assignment (numpy arrays).
  Functions:
    - def split_features_by_fold(all_features: np.ndarray, all_targets: np.ndarray, fold_assignments: np.ndarray, current_fold: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: """ Split all features and targets by fold assignment. Args: all_features: All features array (N_total, feat_dim). all_targets: All targets array (N_total, num_targets). fold_assignments: Fold assignments array (N_total,) with values 0 to n_folds-1. current_fold: Current fold number to split for. Returns: Tuple of (train_features, val_features, train_targets, val_targets). """ if all_features.shape[0] != all_targets.shape[0] or all_features.shape[0] != fold_assignments.shape[0]: raise ValueError(f'Array length mismatch: all_features={all_features.shape[0]}, all_targets={all_targets.shape[0]}, fold_assignments={fold_assignments.shape[0]}') if current_fold < 0: raise ValueError(f'current_fold must be >= 0, got {current_fold}') train_mask = fold_assignments != current_fold val_mask = fold_assignments == current_fold if not np.any(val_mask): raise ValueError(f'No samples found for fold {current_fold}') train_features = all_features[train_mask] val_features = all_features[val_mask] train_targets = all_targets[train_mask] val_targets = all_targets[val_mask] logger.debug(f'Split features for fold {current_fold}: train {train_features.shape}, val {val_features.shape}') return (train_features, val_features, train_targets, val_targets)
  Imports:
    - import numpy as np
    - from typing import Tuple
    - from level_0 import get_logger [internal level_0]
  Line count: 48

### FILE: level_1/data/cv_splits/dataframes.py
  Module docstring: Cross-validation split logic for DataFrames.
  Functions:
    - def create_kfold_splits(data: pd.DataFrame, n_folds: int=5, shuffle: bool=True, random_state: int=42, stratify: Optional[str]=None) -> pd.DataFrame: """ Create K-fold cross-validation splits. Args: data: DataFrame with aggregated data (1 row per image). Must not be empty. n_folds: Number of folds (default: 5). Must be >= 2. shuffle: Whether to shuffle data before splitting (default: True). random_state: Random seed for reproducibility (default: 42). stratify: Optional column name for stratification (e.g., 'State'). If provided, must exist in data.columns. Returns: DataFrame with added 'fold' column (0 to n_folds-1). Each row is assigned to exactly one fold. Raises: ValueError: If data is empty, n_folds is invalid, or stratify column doesn't exist. TypeError: If data is not a DataFrame. """ if not isinstance(data, pd.DataFrame): raise TypeError(f'data must be pandas DataFrame, got {type(data)}') if len(data) == 0: raise ValueError('data cannot be empty') if not isinstance(n_folds, int) or n_folds < 2: raise ValueError(f'n_folds must be integer >= 2, got {n_folds}') if n_folds > len(data): raise ValueError(f'n_folds ({n_folds}) cannot be greater than number of samples ({len(data)})') if stratify is not None: if not isinstance(stratify, str): raise TypeError(f'stratify must be string, got {type(stratify)}') if stratify not in data.columns: raise ValueError(f"stratify column '{stratify}' not found in data.columns") data = data.copy() kfold = KFold(n_splits=n_folds, shuffle=shuffle, random_state=random_state) data['fold'] = None if stratify is not None and stratify in data.columns: skfold = StratifiedKFold(n_splits=n_folds, shuffle=shuffle, random_state=random_state) splitter = skfold.split(data.index, data[stratify]) else: splitter = kfold.split(data.index) for fold_num, (train_idx, val_idx) in enumerate(splitter): data.loc[data.index[val_idx], 'fold'] = fold_num if data['fold'].isna().any(): raise RuntimeError('Some rows were not assigned to a fold') logger.info(f'Created {n_folds}-fold CV splits') logger.info(f"Fold distribution:\n{data['fold'].value_counts().sort_index()}") return data
    - def get_fold_data(data: pd.DataFrame, fold: int, train: bool=True) -> pd.DataFrame: """ Get data for a specific fold (training or validation). Args: data: DataFrame with 'fold' column. Must not be empty. fold: Fold number (0 to n_folds-1). Must be valid fold number. train: If True, return training data (all folds except specified). If False, return validation data (only the specified fold). Returns: Filtered DataFrame containing either training or validation data. Returns empty DataFrame if fold doesn't exist in data. Raises: ValueError: If data is empty, doesn't have 'fold' column, or fold is invalid. TypeError: If data is not a DataFrame. """ if not isinstance(data, pd.DataFrame): raise TypeError(f'data must be pandas DataFrame, got {type(data)}') if len(data) == 0: raise ValueError('data cannot be empty') if 'fold' not in data.columns: raise ValueError("data must have 'fold' column") if not isinstance(fold, int) or fold < 0: raise ValueError(f'fold must be non-negative integer, got {fold}') if train: filtered = data[data['fold'] != fold].copy() logger.debug(f'Fold {fold} training data: {len(filtered)} samples') else: filtered = data[data['fold'] == fold].copy() logger.debug(f'Fold {fold} validation data: {len(filtered)} samples') if len(filtered) == 0: logger.warning(f'No data found for fold {fold} (validation)') return filtered
  Imports:
    - import pandas as pd
    - from sklearn.model_selection import KFold, StratifiedKFold
    - from typing import Optional
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 138

### FILE: level_1/data/domain/__init__.py
  Module docstring: Domain data structures (vision, tabular). Config and models in subpackages.
  Imports:
    - from . import tabular, vision
    - from .tabular import *
    - from .vision import *
  Line count: 11

### FILE: level_1/data/domain/tabular/__init__.py
  Module docstring: Tabular config and dataset.
  Imports:
    - from .config import TabularModelConfig, TabularDataConfig, TabularConfig
    - from .tabular_dataset import TabularDataset
  Line count: 11
  __all__: ['TabularModelConfig', 'TabularDataConfig', 'TabularConfig', 'TabularDataset']

### FILE: level_1/data/domain/tabular/config.py
  Module docstring: Tabular domain configuration.
  Classes:
    - TabularModelConfig
        Methods:
                 def __post_init__(self): if self.input_dim <= 0: raise ValueError('input_dim must be positive') if self.output_dim <= 0: raise ValueError('output_dim must be positive')
    - TabularDataConfig
    - TabularConfig
  Functions:
    - def _default_training() -> TrainingSchema: return TrainingSchema(batch_size=64, epochs=100)
    - def _default_evaluation() -> EvaluationSchema: return EvaluationSchema(metric='f1')
  Imports:
    - from dataclasses import dataclass, field
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import CompositeConfig, EvaluationSchema, PathConfig, TrainingSchema [internal level_0]
  Line count: 54

### FILE: level_1/data/domain/tabular/tabular_dataset.py
  Module docstring: PyTorch Dataset for dense tabular data. Used by MLP and other tabular NN models.
  Classes:
    - TabularDataset
        Methods:
                 def __init__(self, X: np.ndarray, y: Optional[np.ndarray]=None): """ Initialize dataset. Args: X: Feature matrix of shape (n_samples, n_features). y: Optional target matrix of shape (n_samples, n_targets). """ self.X = torch.FloatTensor(X) self.y = torch.FloatTensor(y) if y is not None else None
                 def __len__(self) -> int: return len(self.X)
                 def __getitem__(self, idx: int) -> Tuple[TensorT, Optional[TensorT]]: if self.y is not None: return (self.X[idx], self.y[idx]) return (self.X[idx], None)
  Imports:
    - import numpy as np
    - from typing import Any, Optional, Tuple
    - from layers.layer_0_core.level_0 import get_torch [internal level_0]
  Line count: 34

### FILE: level_1/data/domain/vision/__init__.py
  Module docstring: Vision config and models.
  Imports:
    - from . import models
    - from .config import VisionConfig, VisionDataConfig, VisionModelConfig
    - from .models import *
  Line count: 11

### FILE: level_1/data/domain/vision/config.py
  Module docstring: Vision domain configuration.
  Classes:
    - VisionModelConfig
        Methods:
                 def __post_init__(self): if self.num_classes <= 0: raise ValueError('num_classes must be positive')
    - VisionDataConfig
        Methods:
                 def __post_init__(self): if self.image_size <= 0: raise ValueError('image_size must be positive')
    - VisionConfig
  Functions:
    - def _default_training() -> TrainingSchema: return TrainingSchema(batch_size=32, epochs=30, learning_rate=0.0001)
    - def _default_evaluation() -> EvaluationSchema: return EvaluationSchema(metric='accuracy')
  Imports:
    - from dataclasses import dataclass, field
    - from typing import List, Optional, Tuple
    - from layers.layer_0_core.level_0 import CompositeConfig, EvaluationSchema, PathConfig, TrainingSchema [internal level_0]
  Line count: 70

### FILE: level_1/data/domain/vision/models/__init__.py
  Module docstring: Vision model base, heads, and utilities.
  Imports:
    - from .base_head import BaseHead, ClassificationHead, RegressionHead
    - from .base import BaseVisionModel
    - from .weight_cache import configure_huggingface_cache, resolve_offline_weight_cache
  Line count: 14
  __all__: ['BaseHead', 'ClassificationHead', 'RegressionHead', 'BaseVisionModel', 'configure_huggingface_cache', 'resolve_offline_weight_cache']

### FILE: level_1/data/domain/vision/models/base.py
  Module docstring: Base vision model abstract class.
  Classes:
    - BaseVisionModel
        Methods:
                 def __init__(self): """Initialize base model. Subclasses must call super().__init__().""" super().__init__()
                 @abstractmethod def forward(self, x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]) -> torch.Tensor: """ Forward pass through the model. Args: x: Single tensor (B, C, H, W) or tuple of two tensors for split input. Returns: Output tensor of shape (B, num_classes). """ ...
                 @abstractmethod def get_input_size(self) -> Tuple[int, int]: """Return expected (height, width) input dimensions.""" ...
                 @abstractmethod def freeze_backbone(self) -> None: """Freeze backbone parameters (sets requires_grad=False).""" ...
                 @abstractmethod def unfreeze_backbone(self) -> None: """Unfreeze backbone parameters (sets requires_grad=True).""" ...
                 @abstractmethod def is_pretrained(self) -> bool: """Return True if pretrained weights were successfully loaded.""" ...
                 def save(self, path: str) -> None: """Save model state dict to path.""" if torch is None: raise RuntimeError('PyTorch is required to save vision models.') torch.save(self.state_dict(), path)
                 def load(self, path: str, device: str='cpu') -> None: """Load model state dict from path.""" if torch is None: raise RuntimeError('PyTorch is required to load vision models.') state_dict = torch.load(path, map_location=device) self.load_state_dict(state_dict)
                 def get_num_parameters(self) -> int: """Return total number of model parameters.""" if torch is None: return 0 return sum((p.numel() for p in self.parameters()))
  Imports:
    - from __future__ import annotations
    - from abc import ABC, abstractmethod
    - from typing import Tuple, Union
    - from layers.layer_0_core.level_0 import get_nn_module_base_class, get_torch [internal level_0]
  Line count: 85

### FILE: level_1/data/domain/vision/models/base_head.py
  Module docstring: Base head for vision models (classification/regression).
  Classes:
    - BaseHead
        Methods:
                 def __init__(self, in_features: int, out_features: int, hidden_size: Optional[int]=None, dropout: float=0.3, activation: str='relu'): super().__init__() if torch is None: raise RuntimeError('PyTorch is required to build vision heads.') self.in_features = in_features self.out_features = out_features act_fn = self._get_activation(activation) if hidden_size is None or hidden_size <= 0: self.head = torch.nn.Linear(in_features, out_features) else: self.head = torch.nn.Sequential(torch.nn.Linear(in_features, hidden_size), act_fn, torch.nn.Dropout(dropout), torch.nn.Linear(hidden_size, out_features))
                 def _get_activation(self, activation: str) -> ModuleT: """Return activation module by name.""" if torch is None: raise RuntimeError('PyTorch is required to build vision heads.') activation = activation.lower() if activation == 'relu': return torch.nn.ReLU(inplace=True) if activation == 'gelu': return torch.nn.GELU() if activation == 'silu': return torch.nn.SiLU(inplace=True) raise ValueError(f'Unknown activation: {activation}')
                 def forward(self, x: TensorT) -> TensorT: if torch is None: raise RuntimeError('PyTorch is required to run vision heads.') return self.head(x)
    - ClassificationHead
        Methods:
                 def __init__(self, in_features: int, num_classes: int, hidden_size: Optional[int]=None, dropout: float=0.3, activation: str='relu'): super().__init__(in_features, num_classes, hidden_size=hidden_size, dropout=dropout, activation=activation) self.num_classes = self.out_features
    - RegressionHead
  Imports:
    - from typing import Optional
    - from layers.layer_0_core.level_0 import get_nn_module_base_class, get_torch, get_vision_module_and_tensor_types [internal level_0]
  Line count: 93

### FILE: level_1/data/domain/vision/models/weight_cache.py
  Module docstring: Weight cache resolution for offline and Kaggle environments.
  Functions:
    - def _check_internet_connection() -> bool: """Return True if an outbound internet connection is available.""" try: socket.create_connection(('8.8.8.8', 53), timeout=3) logger.debug('Internet connection detected') return True except OSError: logger.warning('No internet connection detected') return False
    - def configure_huggingface_cache(cache_dir: Path) -> None: """Point HuggingFace cache environment variables at cache_dir.""" os.environ['HF_HOME'] = str(cache_dir) os.environ['TRANSFORMERS_CACHE'] = str(cache_dir) logger.info('Configured HuggingFace cache: %s', cache_dir)
    - def resolve_offline_weight_cache() -> Tuple[Optional[Path], bool]: """ Detect the runtime environment and locate any available offline weights. Returns: (cache_path, has_internet) where cache_path is the first non-empty weight directory found (or None), and has_internet indicates whether an outbound connection is reachable. """ has_internet = _check_internet_connection() if not is_kaggle(): return (None, has_internet) for weight_dir in _KAGGLE_WEIGHT_DIRS: if weight_dir.exists() and any(weight_dir.iterdir()): logger.info('Found Kaggle weight directory: %s', weight_dir) return (weight_dir, has_internet) return (None, has_internet)
  Imports:
    - import os
    - import socket
    - from pathlib import Path
    - from typing import Optional, Tuple
    - from layers.layer_0_core.level_0 import is_kaggle, get_logger [internal level_0]
  Line count: 56

### FILE: level_1/data/io/__init__.py
  Module docstring: Data I/O utilities.
  Imports:
    - from .batch_loading import BatchLoader, load_batch
    - from .numpy_loader import build_embedding_error_message, load_ids_file, load_embeddings_file
  Line count: 12
  __all__: ['BatchLoader', 'load_batch', 'build_embedding_error_message', 'load_ids_file', 'load_embeddings_file']

### FILE: level_1/data/io/batch_loading.py
  Module docstring: Batch loading utilities. Uses level_0 for logging.
  Classes:
    - BatchLoader
        Methods:
                 def __call__(self, paths: Iterable[Union[str, Path]], *, desc: str='Loading', show_progress: bool=False, **kwargs: object) -> List[T]: ...
  Functions:
    - def load_batch(paths: Iterable[Union[str, Path]], loader: Callable[[Union[str, Path]], T], *, desc: str='Loading', show_progress: bool=False, item_name: str='items', raise_on_error: bool=True) -> List[T]: """ Load multiple items by applying a loader to each path. Args: paths: Iterable of file paths. loader: Callable that takes a path and returns a loaded item. desc: Progress bar description when show_progress is True. show_progress: If True, wrap iteration with tqdm when available. item_name: Used in log message, e.g. "CSV files", "images". raise_on_error: If True, raise on first load failure. If False, log and skip. Returns: List of loaded items in path order (skipped items omitted when raise_on_error=False). """ paths_list = list(paths) if not paths_list: return [] iterator = paths_list if show_progress: try: iterator = tqdm(paths_list, desc=desc) except ImportError: logger.debug('tqdm not available; progress disabled') results: List[T] = [] for path in iterator: try: results.append(loader(path)) except Exception as e: if raise_on_error: raise logger.warning('Skipping %s: %s', path, e) logger.info('Loaded %s %s', len(results), item_name) return results
  Imports:
    - from pathlib import Path
    - from typing import Callable, Iterable, List, Protocol, TypeVar, Union
    - from tqdm import tqdm
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 74

### FILE: level_1/data/io/numpy_loader.py
  Module docstring: Load NumPy embeddings and build diagnostic error messages.
  Functions:
    - def build_embedding_error_message(embedding_type: str, datatype: str, base_path: Path, checked_paths: list) -> str: """ Build comprehensive error message for embedding loading failures. Args: embedding_type: Embedding type datatype: 'train' or 'test' base_path: Base path that was checked checked_paths: List of (structure_type, ids_path, embeddings_path) tuples Returns: Error message string """ error_msg = f'Could not load {embedding_type} embeddings for {datatype}.\n\n' error_msg += 'Checked paths:\n' for structure_type, checked_ids_path, checked_embeddings_path in checked_paths: error_msg += f' [{structure_type}]\n' error_msg += f" IDs: {checked_ids_path} {('✓' if checked_ids_path.exists() else '✗')}\n" error_msg += f" Embeddings: {checked_embeddings_path} {('✓' if checked_embeddings_path.exists() else '✗')}\n" error_msg += f'\nDirectory diagnostics:\n' error_msg += f" Base directory: {base_path} {('✓ exists' if base_path.exists() else '✗ does not exist')}\n" if base_path.exists(): try: files = list(base_path.iterdir()) if files: error_msg += f' Files in base directory ({len(files)} found):\n' for f in sorted(files)[:10]: error_msg += f' - {f.name}\n' if len(files) > 10: error_msg += f' ... and {len(files) - 10} more files\n' except PermissionError: error_msg += f' Cannot list files (permission denied)\n' return error_msg
    - def load_ids_file(ids_path: Path) -> np.ndarray: """Load IDs file.""" if not ids_path.exists(): raise FileNotFoundError(f'ID file not found: {ids_path}') return np.load(ids_path)
    - def load_embeddings_file(embeddings_path: Path, embedding_type: str, datatype: str, use_memmap: bool) -> np.ndarray: """Load embeddings file (memmap or full array).""" if not embeddings_path.exists(): raise FileNotFoundError(f'Embeddings file not found: {embeddings_path}') if use_memmap: embeds = np.load(embeddings_path, mmap_mode='r') logger.info(f'Loaded {embedding_type} {datatype} as memmap: {embeds.shape} (dtype: {embeds.dtype})') else: embeds = np.load(embeddings_path) if embeds.dtype != np.float32: embeds = embeds.astype(np.float32) logger.info(f'Loaded {embedding_type} {datatype}: {embeds.shape} (dtype: {embeds.dtype})') return embeds
  Imports:
    - import numpy as np
    - from pathlib import Path
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 81

### FILE: level_1/data/processing/__init__.py
  Module docstring: Data processing (preprocessing, augmentation, transforms, datasets).
  Imports:
    - from . import augmentation, datasets, preprocessing
    - from .augmentation import *
    - from .datasets import *
    - from .preprocessing import *
  Line count: 13

### FILE: level_1/data/processing/augmentation/__init__.py
  Module docstring: Augmentation transforms. Callers pass params (e.g. from contest transform_defaults).
  Imports:
    - from .blur import get_blur_transform
    - from .color import get_color_jitter_transform
    - from .geometric import get_geometric_transform
    - from .noise import AddGaussianNoise, get_noise_transform
    - from .pipeline import compose_transform_pipeline
  Line count: 16
  __all__: ['get_blur_transform', 'get_color_jitter_transform', 'get_geometric_transform', 'AddGaussianNoise', 'get_noise_transform', 'compose_transform_pipeline']

### FILE: level_1/data/processing/augmentation/blur.py
  Module docstring: Blurring augmentations. Callers pass params (e.g. from contest transform_defaults).
  Functions:
    - def get_blur_transform(kernel_size: Union[int, Tuple[int, int]]=3, sigma: Tuple[float, float]=(0.1, 2.0), p: float=1.0) -> transforms.GaussianBlur: """ Get Gaussian blur transform. When p < 1, wraps in RandomApply. Caller passes kernel_size and sigma (contest may use its defaults). """ if isinstance(kernel_size, int): if kernel_size <= 0: raise ValueError(f'kernel_size must be positive, got {kernel_size}') if kernel_size % 2 == 0: kernel_size += 1 logger.debug('kernel_size was even, adjusted to %s', kernel_size) elif isinstance(kernel_size, tuple): if len(kernel_size) != 2: raise ValueError(f'kernel_size tuple must have length 2, got {kernel_size}') kernel_size = tuple((k + 1 if k % 2 == 0 else k for k in kernel_size)) else: raise TypeError(f'kernel_size must be int or tuple, got {type(kernel_size)}') if len(sigma) != 2: raise ValueError(f'sigma must be a tuple of length 2, got {sigma}') if sigma[0] < 0 or sigma[1] < 0: raise ValueError(f'sigma values must be non-negative, got {sigma}') if sigma[0] > sigma[1]: raise ValueError(f'sigma[0] must be <= sigma[1], got {sigma}') t = transforms.GaussianBlur(kernel_size=kernel_size, sigma=sigma) if p < 1.0: return transforms.RandomApply([t], p=p) return t
  Imports:
    - import torchvision.transforms as transforms
    - from typing import Tuple, Union
    - from level_0 import get_logger [internal level_0]
  Line count: 44

### FILE: level_1/data/processing/augmentation/color.py
  Module docstring: Color jittering augmentations. Callers pass params (e.g. from contest transform_defaults).
  Functions:
    - def get_color_jitter_transform(brightness: Optional[float]=0.2, contrast: Optional[float]=0.2, saturation: Optional[float]=0.2, hue: Optional[float]=0.1, p: float=1.0) -> transforms.ColorJitter: """ Get color jitter transform. When p < 1, wraps in RandomApply. Caller passes params. """ if brightness is not None and brightness < 0: raise ValueError(f'brightness must be non-negative, got {brightness}') if contrast is not None and contrast < 0: raise ValueError(f'contrast must be non-negative, got {contrast}') if saturation is not None and saturation < 0: raise ValueError(f'saturation must be non-negative, got {saturation}') if hue is not None and (not 0.0 <= hue <= 0.5): raise ValueError(f'hue must be in [0, 0.5], got {hue}') t = transforms.ColorJitter(brightness=brightness, contrast=contrast, saturation=saturation, hue=hue) if p < 1.0: return transforms.RandomApply([t], p=p) return t
  Imports:
    - import torchvision.transforms as transforms
    - from typing import Optional
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 39

### FILE: level_1/data/processing/augmentation/geometric.py
  Module docstring: Geometric transformation augmentations. Callers pass params (e.g. from contest transform_defaults).
  Functions:
    - def get_geometric_transform(degrees: Union[float, Tuple[float, float]]=15.0, translate: Optional[Tuple[float, float]]=(0.1, 0.1), scale: Optional[Tuple[float, float]]=(0.9, 1.1), shear: Optional[Union[float, Tuple[float, float]]]=5.0, interpolation: transforms.InterpolationMode=transforms.InterpolationMode.BILINEAR, fill: int=0, p: float=1.0) -> transforms.RandomAffine: """ Get geometric transformation (rotation, translation, scale, shear). When p < 1, wraps in RandomApply. Caller passes params. """ if translate is not None: if len(translate) != 2: raise ValueError(f'translate must be a tuple of length 2, got {translate}') if not all((0.0 <= v <= 1.0 for v in translate)): raise ValueError(f'translate values must be in [0, 1], got {translate}') if scale is not None: if len(scale) != 2: raise ValueError(f'scale must be a tuple of length 2, got {scale}') if scale[0] >= scale[1]: raise ValueError(f'scale[0] must be < scale[1], got {scale}') if not all((v > 0 for v in scale)): raise ValueError(f'scale values must be positive, got {scale}') t = transforms.RandomAffine(degrees=degrees, translate=translate, scale=scale, shear=shear, interpolation=interpolation, fill=fill) if p < 1.0: return transforms.RandomApply([t], p=p) return t
  Imports:
    - import torchvision.transforms as transforms
    - from typing import Optional, Tuple, Union
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 48

### FILE: level_1/data/processing/augmentation/noise.py
  Module docstring: Noise addition augmentations. Callers pass params (e.g. from contest transform_defaults).
  Classes:
    - AddGaussianNoise
        Methods:
                 def __init__(self, mean: float=0.0, std: float=0.01, p: float=1.0): super().__init__() if std < 0: raise ValueError(f'std must be non-negative, got {std}') self.mean = mean self.std = std self.p = p
                 def forward(self, tensor: TensorT) -> TensorT: if torch is None: raise RuntimeError('PyTorch is required for AddGaussianNoise.') if self.p < 1.0 and torch.rand(1, device=tensor.device).item() >= self.p: return tensor noise = torch.randn_like(tensor) * self.std + self.mean return torch.clamp(tensor + noise, 0.0, 1.0)
                 def __repr__(self): return f'{self.__class__.__name__}(mean={self.mean}, std={self.std}, p={self.p})'
  Functions:
    - def get_noise_transform(mean: float=0.0, std: float=0.01, p: float=1.0): """ Get Gaussian noise addition transform. Caller passes params (contest may use its defaults). """ return AddGaussianNoise(mean=mean, std=std, p=p)
  Imports:
    - from layers.layer_0_core.level_0 import get_logger, get_nn_module_base_class, get_torch, get_vision_module_and_tensor_types [internal level_0]
  Line count: 50

### FILE: level_1/data/processing/augmentation/pipeline.py
  Module docstring: Transform composition utilities.
  Functions:
    - def compose_transform_pipeline(pil_transforms: Optional[List]=None, tensor_transforms: Optional[List]=None, include_to_tensor: bool=True) -> transforms.Compose: """ Compose a complete transform pipeline from PIL and tensor transforms. Standard pipeline order: 1. PIL Image transforms (preprocessing, augmentation) 2. ToTensor (converts PIL Image to tensor) 3. Tensor transforms (normalization, tensor augmentation) Args: pil_transforms: List of PIL Image transforms to apply before ToTensor. tensor_transforms: List of tensor transforms to apply after ToTensor. include_to_tensor: Whether to include ToTensor transform (default: True). Set to False if ToTensor is already in pil_transforms. Returns: Compose transform with the complete pipeline. Example: >>> from torchvision.transforms import Resize, Normalize >>> pipeline = compose_transform_pipeline( ... pil_transforms=[Resize(224)], ... tensor_transforms=[Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])] ... ) """ transform_list = [] if pil_transforms: transform_list.extend(pil_transforms) logger.debug(f'Added {len(pil_transforms)} PIL transforms') if include_to_tensor: transform_list.append(transforms.ToTensor()) logger.debug('Added ToTensor') if tensor_transforms: transform_list.extend(tensor_transforms) logger.debug(f'Added {len(tensor_transforms)} tensor transforms') logger.debug(f'Composed transform pipeline with {len(transform_list)} total transforms') return transforms.Compose(transform_list)
  Imports:
    - import torchvision.transforms as transforms
    - from typing import List, Optional
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 60

### FILE: level_1/data/processing/datasets/__init__.py
  Module docstring: Image and streaming dataset classes.
  Imports:
    - from .image_datasets import BaseImageDataset, ImagePathDataset
    - from .streaming_datasets import BaseStreamingDataset, StreamingDataset, StreamingSplitDataset
  Line count: 12
  __all__: ['BaseImageDataset', 'ImagePathDataset', 'BaseStreamingDataset', 'StreamingDataset', 'StreamingSplitDataset']

### FILE: level_1/data/processing/datasets/image_datasets.py
  Module docstring: Base image dataset classes for DataFrame-based and path-list loading.
  Classes:
    - BaseImageDataset
        Methods:
                 def __init__(self, data: pd.DataFrame, image_dir: Union[str, Path], image_col: str='image_id', target_cols: Optional[List[str]]=None, transform: Optional[Callable]=None, image_ext: str='.jpg'): self.data = data.reset_index(drop=True) self.image_dir = Path(image_dir) self.image_col = image_col self.target_cols = target_cols or [] self.transform = transform self.image_ext = image_ext if not self.image_dir.exists(): raise FileNotFoundError(f'Image directory not found: {self.image_dir}') if image_col not in data.columns: raise ValueError(f"Column '{image_col}' not found in data. Available: {list(data.columns)}") if target_cols: missing_cols = [col for col in target_cols if col not in data.columns] if missing_cols: raise ValueError(f'Target columns not found in data: {missing_cols}') logger.info(f'Initialized {self.__class__.__name__} with {len(self)} samples') if target_cols: logger.info(f' Target columns: {target_cols}')
                 def __len__(self) -> int: return len(self.data)
                 def __getitem__(self, idx: int) -> Union[Any, Tuple[Any, Any]]: image_id = self.data.iloc[idx][self.image_col] image_path = self.image_dir / f'{image_id}{self.image_ext}' if not image_path.exists(): raise FileNotFoundError(f'Image file not found: {image_path}') try: image = Image.open(image_path).convert('RGB') except Exception as e: raise IOError(f'Error loading image {image_path}: {e}') if self.transform: image = self.transform(image) if self.target_cols: targets = self.data.iloc[idx][self.target_cols].values.astype('float32') targets = torch.tensor(targets) return (image, targets) return image
    - ImagePathDataset
        Methods:
                 def __init__(self, image_paths: List[Union[str, Path]], transform: Optional[Callable]=None): self.image_paths = [Path(p) for p in image_paths] self.transform = transform missing_paths = [p for p in self.image_paths if not p.exists()] if missing_paths: raise FileNotFoundError(f'Found {len(missing_paths)} missing image files. First few: {missing_paths[:5]}') logger.info(f'Initialized {self.__class__.__name__} with {len(self)} images')
                 def __len__(self) -> int: return len(self.image_paths)
                 def __getitem__(self, idx: int) -> Any: image_path = self.image_paths[idx] try: image = Image.open(image_path).convert('RGB') except Exception as e: raise IOError(f'Error loading image {image_path}: {e}') if self.transform: image = self.transform(image) return image
  Imports:
    - import pandas as pd
    - from pathlib import Path
    - from PIL import Image
    - from typing import Any, Optional, Callable, List, Union, Tuple
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal level_0]
  Line count: 119

### FILE: level_1/data/processing/datasets/streaming_datasets.py
  Module docstring: Streaming datasets; load_jpg via PIL; target_cols provided by contest.
  Classes:
    - BaseStreamingDataset
        Methods:
                 def __init__(self, data: pd.DataFrame, data_root: str, transform: Optional[Callable]=None, target_cols: Optional[List[str]]=None, shuffle: bool=False, image_path_column: str='image_path'): self.data_rows = data.reset_index(drop=True).to_dict('records') self.data_root = Path(data_root) self.transform = transform self.shuffle = shuffle self.image_path_column = image_path_column self.target_cols = target_cols or [] if self.data_rows and self.target_cols: req = [image_path_column] + self.target_cols missing = [c for c in req if c not in self.data_rows[0]] if missing: raise ValueError(f'Missing columns: {missing}') self._length = len(self.data_rows)
                 def __len__(self) -> int: return self._length
                 def __iter__(self) -> Iterator: torch = get_torch() worker_info = torch.utils.data.get_worker_info() indices = list(range(len(self.data_rows))) if self.shuffle: random.shuffle(indices) if worker_info is None: for i in indices: yield self._load_item(i) else: nw, wid = (worker_info.num_workers, worker_info.id) for i in indices[wid::nw]: yield self._load_item(i)
                 def _load_item(self, idx: int): raise NotImplementedError
                 def _load_image(self, path: Path): return load_image_pil(path)
                 def _get_targets(self, row: dict): torch = get_torch() return torch.tensor([float(row[c]) for c in self.target_cols], dtype=torch.float32)
    - StreamingDataset
        Methods:
                 def _load_item(self, idx: int): torch = get_torch() row = self.data_rows[idx] path = self.data_root / row[self.image_path_column] img = self._load_image(path) if self.transform: img = self.transform(img) else: img = ToTensor()(img) t = self._get_targets(row) if self.target_cols else torch.zeros(0, dtype=torch.float32) return (img, t)
    - StreamingSplitDataset
        Methods:
                 def _load_item(self, idx: int): torch = get_torch() row = self.data_rows[idx] path = self.data_root / row[self.image_path_column] img = self._load_image(path) w, h = img.size mid = w // 2 left = img.crop((0, 0, mid, h)) right = img.crop((mid, 0, w, h)) if self.transform: left = self.transform(left) right = self.transform(right) else: t = ToTensor() left, right = (t(left), t(right)) tgt = self._get_targets(row) if self.target_cols else torch.zeros(0, dtype=torch.float32) return (left, right, tgt)
  Imports:
    - import random
    - import pandas as pd
    - from pathlib import Path
    - from typing import Callable, Iterator, List, Optional
    - from torchvision.transforms import ToTensor
    - from layers.layer_0_core.level_0 import get_logger, load_image_pil, get_torch [internal level_0]
  Line count: 105

### FILE: level_1/data/processing/preprocessing/__init__.py
  Module docstring: Vision data preprocessing utilities.
  Imports:
    - from .contrast_enhancement import contrast_enhancement
    - from .image_base import crop_relative_height, inpaint_by_hsv_range
    - from .normalization import normalize, get_normalize_transform
    - from .resizing import resize, get_resize_transform
  Line count: 19
  __all__: ['contrast_enhancement', 'crop_relative_height', 'inpaint_by_hsv_range', 'normalize', 'get_normalize_transform', 'resize', 'get_resize_transform']

### FILE: level_1/data/processing/preprocessing/contrast_enhancement.py
  Module docstring: Contrast enhancement. Callers pass method (e.g. from contest defaults).
  Functions:
    - def contrast_enhancement(image: Union[Image.Image, np.ndarray], method: str='histogram_equalization') -> Union[Image.Image, np.ndarray]: """ Enhance image contrast using histogram equalization or CLAHE. Args: image: PIL Image or numpy array. method: Enhancement method ('histogram_equalization', 'clahe'). Returns: Enhanced image of the same type as input. """ if method not in _VALID_METHODS: raise ValueError(f"Invalid method '{method}'. Must be one of: {', '.join(_VALID_METHODS)}") if isinstance(image, Image.Image): img_array = np.array(image) is_pil = True else: img_array = np.asarray(image) is_pil = False if img_array.dtype != np.uint8: img_array = (img_array * 255).astype(np.uint8) if img_array.max() <= 1.0 else img_array.astype(np.uint8) if len(img_array.shape) == 2: if method == 'histogram_equalization': enhanced = cv2.equalizeHist(img_array) else: clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) enhanced = clahe.apply(img_array) elif len(img_array.shape) == 3: enhanced = np.zeros_like(img_array) if method == 'histogram_equalization': for i in range(img_array.shape[2]): enhanced[:, :, i] = cv2.equalizeHist(img_array[:, :, i]) else: clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)) for i in range(img_array.shape[2]): enhanced[:, :, i] = clahe.apply(img_array[:, :, i]) else: raise ValueError(f'Unsupported image shape: {img_array.shape}') if is_pil: return Image.fromarray(enhanced) return enhanced
  Imports:
    - import numpy as np
    - import cv2
    - from PIL import Image
    - from typing import Union
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 73

### FILE: level_1/data/processing/preprocessing/image_base.py
  Module docstring: Generic image preprocessing utilities.
  Functions:
    - def crop_relative_height(img: np.ndarray, keep_ratio: float) -> np.ndarray: """ Crop image vertically by keeping top portion. Args: img: Image array (H, W, C) keep_ratio: Fraction of height to keep (0 < keep_ratio <= 1) Returns: Cropped image """ if not 0 < keep_ratio <= 1.0: raise ValueError('keep_ratio must be in (0, 1]') h = img.shape[0] cutoff = int(h * keep_ratio) return img[:cutoff, :]
    - def inpaint_by_hsv_range(img: np.ndarray, lower: Tuple[int, int, int], upper: Tuple[int, int, int], kernel_size: int=3, iterations: int=2, radius: int=3) -> np.ndarray: """ Inpaint pixels in given HSV range. Args: img: RGB image lower: Lower HSV bound upper: Upper HSV bound kernel_size: Dilation kernel size iterations: Dilation iterations radius: Inpainting radius Returns: Inpainted image """ hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV) mask = cv2.inRange(hsv, np.array(lower), np.array(upper)) if kernel_size > 0 and iterations > 0: kernel = np.ones((kernel_size, kernel_size), np.uint8) mask = cv2.dilate(mask, kernel, iterations=iterations) if np.any(mask): img = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA) return img
  Imports:
    - import cv2
    - import numpy as np
    - from typing import Tuple
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 80

### FILE: level_1/data/processing/preprocessing/normalization.py
  Module docstring: Image normalization using ImageNet statistics.
  Functions:
    - def normalize(tensor: Any, mean: Tuple[float, float, float]=IMAGENET_MEAN, std: Tuple[float, float, float]=IMAGENET_STD) -> Any: """ Normalize tensor using mean and standard deviation per channel. Args: tensor: Input tensor (C, H, W) or (B, C, H, W), range [0, 1]. mean: Mean per channel (default: ImageNet mean). std: Std per channel (default: ImageNet std). Returns: Normalized tensor of the same shape. """ if not isinstance(tensor, torch.Tensor): raise TypeError(f'tensor must be torch.Tensor, got {type(tensor)}') if len(mean) != 3: raise ValueError(f'mean must be a tuple of length 3, got {mean}') if len(std) != 3: raise ValueError(f'std must be a tuple of length 3, got {std}') if any((s <= 0 for s in std)): raise ValueError(f'std values must be positive, got {std}') normalize_transform = transforms.Normalize(mean=mean, std=std) return normalize_transform(tensor)
    - def get_normalize_transform(mean: Tuple[float, float, float]=IMAGENET_MEAN, std: Tuple[float, float, float]=IMAGENET_STD) -> Any: """ Get a torchvision Normalize transform for use in transform pipelines. Args: mean: Mean per channel (default: ImageNet mean). std: Std per channel (default: ImageNet std). Returns: Normalize transform instance. """ if len(mean) != 3: raise ValueError(f'mean must be a tuple of length 3, got {mean}') if len(std) != 3: raise ValueError(f'std must be a tuple of length 3, got {std}') if any((s <= 0 for s in std)): raise ValueError(f'std values must be positive, got {std}') return transforms.Normalize(mean=mean, std=std)
  Imports:
    - import torchvision.transforms as transforms
    - from typing import Any, Tuple
    - from layers.layer_0_core.level_0 import get_logger, get_torch, IMAGENET_MEAN, IMAGENET_STD [internal level_0]
  Line count: 63

### FILE: level_1/data/processing/preprocessing/resizing.py
  Module docstring: Image resizing utilities for transform pipelines.
  Functions:
    - def resize(image: Image.Image, size: Union[int, Tuple[int, int]], interpolation: int=Image.BILINEAR) -> Image.Image: """ Resize image to specified size. Args: image: PIL Image to resize. size: Target size. If int, creates square (size, size). If tuple (height, width), uses exact dimensions. interpolation: Interpolation method (default: Image.BILINEAR). Returns: Resized PIL Image with the specified dimensions. Raises: ValueError: If size is invalid (non-positive values). TypeError: If image is not a PIL Image or size has invalid type. """ if not isinstance(image, Image.Image): raise TypeError(f'image must be PIL Image, got {type(image)}') if isinstance(size, int): if size <= 0: raise ValueError(f'size must be positive, got {size}') size = (size, size) elif isinstance(size, tuple): if len(size) != 2: raise ValueError(f'size tuple must have length 2, got {size}') height, width = size if height <= 0 or width <= 0: raise ValueError(f'size dimensions must be positive, got {size}') else: raise TypeError(f'size must be int or tuple (int, int), got {type(size)}') return image.resize(size, interpolation)
    - def get_resize_transform(size: Union[int, Tuple[int, int]], interpolation: int=Image.BILINEAR) -> transforms.Resize: """ Get a torchvision Resize transform for use in transform pipelines. Args: size: Target size. If int, creates square (size, size). If tuple (height, width), uses exact dimensions. interpolation: Interpolation method (default: Image.BILINEAR). Returns: Resize transform instance for torchvision transform pipelines. """ if isinstance(size, int): if size <= 0: raise ValueError(f'size must be positive, got {size}') elif isinstance(size, tuple): if len(size) != 2: raise ValueError(f'size tuple must have length 2, got {size}') height, width = size if height <= 0 or width <= 0: raise ValueError(f'size dimensions must be positive, got {size}') else: raise TypeError(f'size must be int or tuple (int, int), got {type(size)}') return transforms.Resize(size, interpolation=interpolation)
  Imports:
    - import torchvision.transforms as transforms
    - from PIL import Image
    - from typing import Union, Tuple
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 84

### FILE: level_1/evaluation/__init__.py
  Module docstring: Evaluation package for metrics and losses.
  Imports:
    - from .loss_types import LossType, BaseLoss, FocalLoss, WeightedBCELoss, SparseBCEWithLogitsLoss, LabelSmoothingBCEWithLogitsLoss
    - from .metric_registry import MetricRegistry, register_metric, get_metric, list_metrics
    - from .results_analysis import calculate_fold_statistics, generate_cv_test_gap_warnings
  Line count: 35
  __all__: ['LossType', 'BaseLoss', 'FocalLoss', 'WeightedBCELoss', 'SparseBCEWithLogitsLoss', 'LabelSmoothingBCEWithLogitsLoss', 'MetricRegistry', 'register_metric', 'get_metric', 'list_metrics', 'calculate_fold_statistics', 'generate_cv_test_gap_warnings']

### FILE: level_1/evaluation/loss_types.py
  Module docstring: Unified loss functions for tabular and vision models.
  Module-level types / aliases:
    - LossType = Literal['mse', 'mae', 'l1', 'huber', 'smooth_l1', 'bce', 'focal', 'weighted_bce', 'sparse_bce', 'label_smoothing']
  Classes:
    - BaseLoss
        Methods:
                 def __init__(self, reduction: str='mean'): super().__init__() self.reduction = reduction
                 @abstractmethod def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor: """Compute loss. Subclasses must implement.""" ...
    - FocalLoss
        Methods:
                 def __init__(self, alpha: Optional[float]=None, gamma: float=2.0, reduction: str='mean'): """ Initialize Focal Loss. Args: alpha: Weighting factor in range [0,1] to balance positive/negative examples. None means no weighting (default). gamma: Focusing parameter for modulating loss. Higher values down-weight easy examples more. Typical values: [0, 5], commonly 2.0. reduction: Specifies the reduction to apply: 'none' | 'mean' | 'sum'. """ super().__init__(reduction=reduction) self.alpha = alpha self.gamma = gamma
                 def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor: """ Calculate focal loss. Args: inputs: Predictions (logits), shape (N, C) or (N,). targets: Ground truth labels, same shape as inputs. Returns: Focal loss value. """ bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none') probs = torch.sigmoid(inputs) pt = torch.where(targets == 1, probs, 1 - probs) focal_term = (1 - pt) ** self.gamma loss = focal_term * bce_loss if self.alpha is not None: alpha_t = torch.where(targets == 1, torch.tensor(self.alpha, device=targets.device), torch.tensor(1 - self.alpha, device=targets.device)) loss = alpha_t * loss if self.reduction == 'mean': return loss.mean() elif self.reduction == 'sum': return loss.sum() else: return loss
    - WeightedBCELoss
        Methods:
                 def __init__(self, weights: Optional[torch.Tensor]=None, reduction: str='mean'): """ Initialize Weighted BCE Loss. Args: weights: Class weights. Can be: - None: No weighting (default) - 1D tensor of shape (C,): Per-class weights - 2D tensor same shape as targets: Per-sample weights reduction: Specifies the reduction to apply: 'none' | 'mean' | 'sum'. """ super().__init__(reduction=reduction) self.weights = weights
                 def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor: """ Calculate weighted BCE loss. Args: inputs: Predictions (logits). targets: Ground truth labels. Returns: Weighted BCE loss value. """ loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none') if self.weights is not None: if self.weights.dim() == 1: weights = self.weights.unsqueeze(0) loss = loss * weights else: loss = loss * self.weights if self.reduction == 'mean': return loss.mean() elif self.reduction == 'sum': return loss.sum() else: return loss
    - SparseBCEWithLogitsLoss
        Methods:
                 def __init__(self, pos_weight: Optional[torch.Tensor]=None, reduction: str='mean'): """ Initialize Sparse BCE Loss. Args: pos_weight: Weight for positive examples. Can be: - None: No weighting (default) - 1D tensor of shape (C,): Per-class positive weights """ super().__init__(reduction=reduction) self.pos_weight = pos_weight
                 def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor: """ Calculate sparse BCE loss. Args: inputs: Predictions (logits), shape (N, C). targets: Sparse ground truth labels, shape (N, C). Returns: BCE loss value. """ return F.binary_cross_entropy_with_logits(inputs, targets, pos_weight=self.pos_weight, reduction=self.reduction)
    - LabelSmoothingBCEWithLogitsLoss
        Methods:
                 def __init__(self, smoothing: float=0.1, reduction: str='mean'): """ Initialize Label Smoothing BCE Loss. Args: smoothing: Smoothing factor in range [0, 1]. 0 = no smoothing (hard labels) Higher values = more smoothing Typical values: 0.05 - 0.2 reduction: Specifies the reduction to apply: 'none' | 'mean' | 'sum'. """ super().__init__(reduction=reduction) if not 0 <= smoothing < 1: raise ValueError(f'smoothing must be in [0, 1), got {smoothing}') self.smoothing = smoothing
                 def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor: """ Calculate label smoothed BCE loss. Args: inputs: Predictions (logits). targets: Ground truth labels (0 or 1). Returns: Label smoothed BCE loss value. """ targets_smooth = targets * (1 - self.smoothing) + self.smoothing / 2 loss = F.binary_cross_entropy_with_logits(inputs, targets_smooth, reduction=self.reduction) return loss
  Imports:
    - from abc import ABC, abstractmethod
    - from typing import Literal, Optional
    - from layers.layer_0_core.level_0 import get_torch [internal level_0]
  Line count: 303
  __all__: ['LossType', 'BaseLoss', 'FocalLoss', 'WeightedBCELoss', 'SparseBCEWithLogitsLoss', 'LabelSmoothingBCEWithLogitsLoss']

### FILE: level_1/evaluation/metric_registry.py
  Module docstring: Metric registry.
  Classes:
    - MetricRegistry
        Methods:
                 def __init__(self): self._metrics: Dict[str, Metric] = {}
                 def register(self, metric: Metric) -> None: if metric.name in self._metrics: logger.warning("Metric '%s' already registered, overwriting", metric.name) self._metrics[metric.name] = metric logger.debug('Registered metric: %s', metric.name)
                 def get(self, name: str) -> Optional[Metric]: return self._metrics.get(name)
                 def list_metrics(self) -> list: return list(self._metrics.keys())
                 def __contains__(self, name: str) -> bool: return name in self._metrics
                 def __repr__(self) -> str: return f'MetricRegistry(metrics={list(self._metrics.keys())})'
  Functions:
    - def register_metric(metric: Metric) -> None: _global_registry.register(metric)
    - def get_metric(name: str) -> Optional[Metric]: return _global_registry.get(name)
    - def list_metrics() -> list: return _global_registry.list_metrics()
  Imports:
    - from typing import Dict, Optional
    - from level_0 import Metric, get_logger [internal level_0]
  Line count: 47

### FILE: level_1/evaluation/results_analysis.py
  Module docstring: Results analysis: fold statistics and CV-test gap warnings.
  Functions:
    - def calculate_fold_statistics(fold_scores: List[float]) -> Dict[str, float]: """ Calculate statistics for fold scores. Args: fold_scores: List of fold scores Returns: Dictionary with fold statistics """ fold_mean = statistics.mean(fold_scores) fold_std = statistics.stdev(fold_scores) if len(fold_scores) > 1 else 0.0 fold_min = min(fold_scores) fold_max = max(fold_scores) fold_range = fold_max - fold_min return {'fold_mean': fold_mean, 'fold_std': fold_std, 'fold_min': fold_min, 'fold_max': fold_max, 'fold_range': fold_range}
    - def generate_cv_test_gap_warnings(cv_score: float, fold_mean: float, fold_range: float, test_score: Optional[float], threshold: float) -> List[str]: """ Generate warning messages for CV-test gap analysis. Args: cv_score: Average CV score fold_mean: Mean of fold scores fold_range: Range of fold scores test_score: Optional test score threshold: Gap threshold Returns: List of warning messages """ warnings = [] if fold_range > 0.2: warnings.append(f'⚠️ Large fold score range detected ({fold_range:.4f}). This suggests high variance in model performance across folds.') if abs(cv_score - fold_mean) > 1e-06: warnings.append(f"⚠️ CV score ({cv_score:.6f}) doesn't match fold mean ({fold_mean:.6f}). This may indicate an error in score calculation.") if test_score is not None: cv_test_gap = cv_score - test_score if cv_test_gap > threshold: warnings.append(f'⚠️ Large CV-test gap detected ({cv_test_gap:.4f}, threshold: {threshold}). CV score ({cv_score:.4f}) is much higher than test score ({test_score:.4f}). This may indicate overfitting. Possible causes: overfitting to validation folds, distribution shift, or model instability.') logger.warning(f'⚠️ Large CV-test gap detected: {cv_test_gap:.4f} (threshold: {threshold}). This may indicate overfitting. CV: {cv_score:.4f}, Test: {test_score:.4f}') elif cv_test_gap < -0.1: warnings.append(f'⚠️ Test score ({test_score:.4f}) is much higher than CV score ({cv_score:.4f}). This is unusual and may indicate issues with validation set or test set leakage.') return warnings
  Imports:
    - import statistics
    - from typing import List, Optional, Dict
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 94

### FILE: level_1/features/__init__.py
  Module docstring: Feature extraction framework: cache, registry, extraction base, and embedding pipeline.
  Imports:
    - from . import cache
    - from .cache import *
    - from .base_feature_extractor import BaseFeatureExtractor
    - from .feature_registry import INDIVIDUAL_FEATURES, FEATURE_PRESETS, get_feature_preset, parse_feature_spec
    - from .film import FiLM
    - from .fuse_embeddings import fuse_embeddings
    - from .physicochemical_features import calculate_physicochemical_properties, calculate_ctd_features
    - from .siglip_classes import get_siglip_image_classes, get_siglip_text_classes
  Line count: 36

### FILE: level_1/features/base_feature_extractor.py
  Module docstring: Base for feature extractors: shared device handling and optional progress wrapping.
  Classes:
    - BaseFeatureExtractor
        Methods:
                 def __init__(self, device: Optional[torch.device]=None) -> None: if torch is not None: self.device = device if device is not None else torch.device('cuda' if torch.cuda.is_available() else 'cpu') else: self.device = device
                 @abstractmethod def extract_features(self, *args: Any, **kwargs: Any) -> Any: """ Extract features from input. Signature and return type are implementation-defined. Subclasses must implement this for a consistent public interface. """ ...
                 def _wrap_with_progress(self, iterable: Iterable[T], desc: str, show_progress: bool) -> Iterable[T]: """Wrap iterable with tqdm if show_progress and tqdm is available.""" if not show_progress: return iterable try: return tqdm(iterable, desc=desc) except ImportError: logger.debug('tqdm not available; progress disabled') return iterable
  Imports:
    - from abc import ABC, abstractmethod
    - from typing import Any, Iterable, Optional, TypeVar
    - from tqdm.auto import tqdm
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal level_0]
  Line count: 49

### FILE: level_1/features/cache/__init__.py
  Module docstring: Feature cache management.
  Imports:
    - from .config import set_feature_cache_path_provider, set_model_id_map, get_model_id, get_cache_base_paths, get_model_name_from_model_id, get_metadata_dir
    - from .filename import generate_feature_filename, parse_feature_filename
  Line count: 24
  __all__: ['set_feature_cache_path_provider', 'set_model_id_map', 'get_model_id', 'get_cache_base_paths', 'get_model_name_from_model_id', 'get_metadata_dir', 'generate_feature_filename', 'parse_feature_filename']

### FILE: level_1/features/cache/config.py
  Module docstring: Runtime configuration for the feature cache: path provider and model ID map.
  Module-level types / aliases:
    - _feature_cache_path_provider: Optional[Callable[[], Any]]
    - _model_id_map: Optional[Dict[str, str]]
  Functions:
    - def set_feature_cache_path_provider(provider: Optional[Callable[[], Any]]) -> None: """Register the path provider for the feature cache. Args: provider: Callable returning an object with .input_base and .working_base Path attributes. Pass None to revert to default paths. """ global _feature_cache_path_provider _feature_cache_path_provider = provider
    - def set_model_id_map(model_id_map: Optional[Dict[str, str]]) -> None: """Register the model name → model_id mapping. Must be called by the contest layer at startup before any filename resolution that requires model name lookup. Args: model_id_map: Dict mapping model_name → model_id string. """ global _model_id_map _model_id_map = model_id_map
    - def get_model_id(model_name: str) -> str: """Forward-look up the model_id for a given model_name. Raises: RuntimeError: If set_model_id_map() has not been called. ValueError: If model_name is not present in the registered map. """ if _model_id_map is None: raise RuntimeError('model_id_map not set. Contest layer must call set_model_id_map() at startup.') key = str(model_name) if key not in _model_id_map: available = ', '.join(sorted(_model_id_map.keys())) raise ValueError(f'Model name {key!r} not found in model_id_map. Available model names: {available}') return _model_id_map[key]
    - def get_cache_base_paths() -> Tuple[Path, Path]: """Return (input_base, working_base) for the feature cache. Uses the registered path provider if set; falls back to local defaults. """ if _feature_cache_path_provider is not None: paths = _feature_cache_path_provider() return (paths.input_base, paths.working_base) return (Path('features_cache') / 'input', Path('features_cache') / 'working')
    - def get_model_name_from_model_id(model_id: str) -> str: """Reverse-look up the model name for a given model_id. Raises: RuntimeError: If set_model_id_map() has not been called. ValueError: If model_id is not present in the registered map. """ if _model_id_map is None: raise RuntimeError('model_id_map not set. Contest layer must call set_model_id_map() at startup.') for model_name, mapped_id in _model_id_map.items(): if mapped_id == model_id: return model_name available_ids = ', '.join(sorted(set(_model_id_map.values()))) raise ValueError(f'Model ID {model_id!r} not found in model_id_map. Available model IDs: {available_ids}')
    - def get_metadata_dir() -> Optional[Path]: """Resolve the combo metadata directory from the registered path provider. Returns None if the provider is not registered or the directory cannot be determined. The contest layer is responsible for registering a provider that exposes metadata_dir or kaggle_metadata_dataset_name. Returns: Path to the metadata directory, or None. """ if _feature_cache_path_provider is None: return None paths = _feature_cache_path_provider() if getattr(paths, 'metadata_dir', None) is not None: return paths.metadata_dir kaggle_name = getattr(paths, 'kaggle_metadata_dataset_name', None) if kaggle_name and is_kaggle(): return Path('/kaggle/input') / kaggle_name return None
  Imports:
    - from pathlib import Path
    - from typing import Any, Callable, Dict, Optional, Tuple
    - from layers.layer_0_core.level_0 import get_logger, is_kaggle [internal level_0]
  Line count: 115

### FILE: level_1/features/cache/filename.py
  Module docstring: Codec for feature cache filenames: encode (model_id, combo_id) → filename and back.
  Functions:
    - def generate_feature_filename(model_id: str, combo_id: str='combo_00') -> str: """Encode (model_id, combo_id) into a canonical feature cache filename. Args: model_id: Two-character model identifier string. combo_id: Combo identifier in the format 'combo_XX'. Defaults to 'combo_00'. Returns: Filename string, e.g. 'variant_0100_features.npz'. Raises: ValueError: If combo_id format is invalid. """ if not combo_id.startswith('combo_'): raise ValueError(f'Invalid combo_id format: {combo_id!r}. Expected format: combo_XX') try: combo_numeric = combo_id.replace('combo_', '') combo_numeric_2digit = f'{int(combo_numeric):02d}' except ValueError: raise ValueError(f'Invalid combo_id numeric part: {combo_id!r}') filename = f'variant_{model_id}{combo_numeric_2digit}_features.npz' logger.debug(f'Generated feature filename: {filename} (model_id={model_id}, combo_id={combo_id})') return filename
    - def parse_feature_filename(filename: str) -> tuple[str, str]: """Decode a canonical feature cache filename into (model_id, combo_id). Args: filename: Filename string, e.g. 'variant_0100_features.npz'. Returns: Tuple of (model_id, combo_id). Raises: ValueError: If filename does not match the expected format. """ if not filename.startswith('variant_'): raise ValueError(f'Invalid feature filename: {filename!r}. Expected format: variant_XXXX_features.npz') if not filename.endswith('_features.npz'): raise ValueError(f'Invalid feature filename: {filename!r}. Expected format: variant_XXXX_features.npz') middle_part = filename.replace('variant_', '').replace('_features.npz', '') if len(middle_part) != 4: raise ValueError(f"Invalid feature filename: {filename!r}. Expected exactly 4 characters between 'variant_' and '_features.npz'") model_id = middle_part[:2] combo_id = f'combo_{middle_part[2:]}' return (model_id, combo_id)
  Imports:
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 60

### FILE: level_1/features/feature_registry.py
  Module docstring: Generic registry of individual features and named feature presets.
  Module-level types / aliases:
    - INDIVIDUAL_FEATURES: Dict[str, Dict[str, Any]]
    - FEATURE_PRESETS: Dict[str, Dict[str, Any]]
  Functions:
    - def get_feature_preset(preset_name: str) -> Dict[str, Any]: """ Return a copy of the named feature preset configuration. """ if preset_name not in FEATURE_PRESETS: raise ValueError(f'Unknown preset: {preset_name!r}. Available presets: {list(FEATURE_PRESETS.keys())}') preset = FEATURE_PRESETS[preset_name].copy() if preset.get('dimensions') is None: preset['dimensions'] = _calculate_dimensions(preset['features']) return preset
    - def parse_feature_spec(feature_spec: str) -> List[str]: """ Parse a feature specification string into a list of feature keys. """ if feature_spec in FEATURE_PRESETS: return FEATURE_PRESETS[feature_spec]['features'] features = [f.strip() for f in feature_spec.split(',') if f.strip()] unknown = [f for f in features if f not in INDIVIDUAL_FEATURES] if unknown: raise ValueError(f'Unknown feature(s): {unknown}. Available features: {list(INDIVIDUAL_FEATURES.keys())} or presets: {list(FEATURE_PRESETS.keys())}') return features
    - def _calculate_dimensions(features: List[str]) -> int: """ Compute total feature dimensionality. """ total = 0 for feat in features: dims = INDIVIDUAL_FEATURES.get(feat, {}).get('dimensions') if dims is None: logger.warning('Feature %r has no known dimensions; skipping', feat) continue total += dims return total
  Imports:
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 94

### FILE: level_1/features/film.py
  Module docstring: FiLM (Feature-wise Linear Modulation) fusion module.
  Classes:
    - FiLM
        Methods:
                 def __init__(self, feat_dim: int): """ Initialize FiLM module. Args: feat_dim: Feature dimension (input and output dimension) """ super().__init__() if torch is None: raise RuntimeError('PyTorch is required for FiLM.') self.feat_dim = feat_dim self.mlp = torch.nn.Sequential(torch.nn.Linear(feat_dim, feat_dim // 2), torch.nn.ReLU(inplace=True), torch.nn.Linear(feat_dim // 2, feat_dim * 2))
                 def forward(self, context: torch.Tensor) -> tuple: """ Generate gamma and beta from context features. Args: context: Context features of shape (B, feat_dim) Returns: Tuple of (gamma, beta), each of shape (B, feat_dim) """ gamma_beta = self.mlp(context) gamma, beta = torch.chunk(gamma_beta, 2, dim=1) return (gamma, beta)
  Imports:
    - from __future__ import annotations
    - from layers.layer_0_core.level_0 import get_logger, get_nn_module_base_class, get_torch [internal level_0]
  Line count: 56

### FILE: level_1/features/fuse_embeddings.py
  Module docstring: Embedding fusion utilities.
  Functions:
    - def _align_embeddings_to_common_ids(embedding_list: List[Tuple[np.ndarray, List[str]]], common_ids: List[str]) -> List[np.ndarray]: """Align each embedding array to common IDs.""" aligned = [] for embeds, ids in embedding_list: aligned_embeds, _ = align_embeddings(embeds, ids, common_ids) aligned.append(aligned_embeds) return aligned
    - def fuse_embeddings(embedding_list: List[Tuple[np.ndarray, List[str]]], target_ids: List[str]) -> Tuple[np.ndarray, List[str]]: """ Align and concatenate multiple embeddings. """ if not embedding_list: return (np.array([]), []) common_ids = find_common_ids(embedding_list, target_ids) if not common_ids: return (np.array([]), []) aligned = _align_embeddings_to_common_ids(embedding_list, common_ids) fused = np.hstack(aligned) return (fused, common_ids)
  Imports:
    - import numpy as np
    - from typing import List, Tuple
    - from layers.layer_0_core.level_0 import align_embeddings, find_common_ids [internal level_0]
  Line count: 50

### FILE: level_1/features/physicochemical_features.py
  Module docstring: Physicochemical and CTD feature extraction for amino acid sequences.
  Functions:
    - def calculate_physicochemical_properties(seq: str) -> np.ndarray: """ Compute 8 physicochemical properties from an amino acid sequence. Properties (in order): 1. log(molecular weight) — log1p of summed residue weights 2. Aliphatic index — weighted fraction of A, V, I, L 3. Instability index — simplified fraction of DEKRH residues × 100 4. Positive fraction — fraction of RKH residues 5. Negative fraction — fraction of DE residues 6. Net charge — positive minus negative fractions 7. GRAVY score — mean Kyte-Doolittle hydropathy 8. Aromaticity — fraction of FWY residues Args: seq: Amino acid sequence string. Returns: Float32 array of 8 values. Zero array if seq is empty. """ if not seq: return np.zeros(8, dtype=np.float32) aa_counts = Counter(seq) length = len(seq) mol_weight = sum((count * AA_WEIGHTS.get(aa, 0.0) for aa, count in aa_counts.items())) aliphatic = (aa_counts.get('A', 0) + 2.9 * aa_counts.get('V', 0) + 3.9 * (aa_counts.get('I', 0) + aa_counts.get('L', 0))) / length instability = sum((aa_counts.get(aa, 0) for aa in 'DEKRH')) / length * 100 positive = sum((aa_counts.get(aa, 0) for aa in 'RKH')) / length negative = sum((aa_counts.get(aa, 0) for aa in 'DE')) / length net_charge = positive - negative gravy = sum((count * HYDROPATHY_VALUES.get(aa, 0.0) for aa, count in aa_counts.items())) / length aromaticity = sum((aa_counts.get(aa, 0) for aa in 'FWY')) / length return np.array([np.log1p(mol_weight), aliphatic, instability, positive, negative, net_charge, gravy, aromaticity], dtype=np.float32)
    - def calculate_ctd_features(seq: str) -> np.ndarray: """ Compute Composition-Transition-Distribution (CTD) features. Feature layout (17 total): Composition (8): fraction of residues in each of the 8 AA_GROUPS. Transition (3): fraction of adjacent-residue group changes, computed for the first 3 AA_GROUPS. Distribution (6): normalised first / middle / last occurrence positions, computed for the first 2 AA_GROUPS (3 positions each). NOTE: The original monolithic file documented 21 CTD features. The actual implementation produces 17 (8 + 3 + 6). This is the correct value; HANDCRAFTED_FEATURE_DIM in amino_acid_constants reflects this. Args: seq: Amino acid sequence string. Returns: Float32 array of 17 CTD values. Zero array if seq is empty. """ if not seq: return np.zeros(17, dtype=np.float32) group_list = list(AA_GROUPS.values()) features: list = [] for group_aas in group_list: features.append(sum((1 for aa in seq if aa in group_aas)) / len(seq)) for group_aas in group_list[:3]: transitions = sum((1 for i in range(len(seq) - 1) if (seq[i] in group_aas) != (seq[i + 1] in group_aas))) features.append(transitions / (len(seq) - 1) if len(seq) > 1 else 0.0) for group_aas in group_list[:2]: positions = [i for i, aa in enumerate(seq) if aa in group_aas] if positions: features.extend([positions[0] / len(seq), positions[len(positions) // 2] / len(seq), positions[-1] / len(seq)]) else: features.extend([0.0, 0.0, 0.0]) return np.array(features, dtype=np.float32)
  Imports:
    - from collections import Counter
    - import numpy as np
    - from layers.layer_0_core.level_0 import AA_GROUPS, AA_WEIGHTS, HYDROPATHY_VALUES [internal level_0]
  Line count: 115

### FILE: level_1/features/siglip_classes.py
  Module docstring: Lazy accessors for SigLIP-related transformer classes.
  Functions:
    - def get_siglip_image_classes() -> Tuple[Optional[Any], Optional[Any]]: """Return (AutoModel, AutoImageProcessor) from the transformers library. Returns: Tuple of (AutoModel, AutoImageProcessor), or (None, None) if the transformers library is not installed. """ try: from transformers import AutoModel, AutoImageProcessor return (AutoModel, AutoImageProcessor) except ImportError: logger.warning('transformers not available. SigLIP image extraction disabled.') return (None, None)
    - def get_siglip_text_classes() -> Tuple[Optional[Any], Optional[Any]]: """Return (AutoModel, AutoTokenizer) from the transformers library. Returns: Tuple of (AutoModel, AutoTokenizer), or (None, None) if the transformers library is not installed. """ try: from transformers import AutoModel, AutoTokenizer return (AutoModel, AutoTokenizer) except ImportError: logger.warning('transformers not available. SigLIP text extraction disabled.') return (None, None)
  Imports:
    - from typing import Any, Optional, Tuple
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 42

### FILE: level_1/grid_search/__init__.py
  Module docstring: Pareto and grid helpers composed above level_0.
  Imports:
    - from .pareto_frontier import get_pareto_frontier
  Line count: 5
  __all__: ['get_pareto_frontier']

### FILE: level_1/grid_search/pareto_frontier.py
  Module docstring: Pareto-optimal result selection for multi-objective optimization.
  Functions:
    - def _dominates(other: Dict[str, Any], candidate: Dict[str, Any], metric_keys: List[str], maximize: List[bool]) -> bool: """True if other dominates candidate (better or equal in all, strictly better in at least one).""" strictly_better_in_any = False for metric, should_max in zip(metric_keys, maximize): candidate_val = candidate.get(metric, worst_case_metric_sentinel(should_max)) other_val = other.get(metric, worst_case_metric_sentinel(should_max)) if should_max: if other_val > candidate_val: strictly_better_in_any = True elif other_val < candidate_val: return False elif other_val < candidate_val: strictly_better_in_any = True elif other_val > candidate_val: return False return strictly_better_in_any
    - def get_pareto_frontier(results: List[Dict[str, Any]], metric_keys: List[str], maximize: List[bool]) -> List[Dict[str, Any]]: """ Get Pareto-optimal results for multi-objective optimization. Returns results that are not dominated by any other result across all specified metrics. Args: results: List of result dictionaries metric_keys: List of metric keys to consider maximize: List of bools indicating if each metric should be maximized Returns: List of Pareto-optimal results Example: >>> # Trade-off between accuracy (max) and latency (min) >>> pareto = get_pareto_frontier( ... results, ... metric_keys=['accuracy', 'latency_ms'], ... maximize=[True, False] ... ) """ if not results: raise ValueError('Results list cannot be empty') if len(metric_keys) != len(maximize): raise ValueError('metric_keys and maximize must have same length') successful = filter_successful_results(results) if not successful: return [] pareto_optimal = [] for candidate in successful: is_dominated = False for other in successful: if candidate is other: continue if _dominates(other, candidate, metric_keys, maximize): is_dominated = True break if not is_dominated: pareto_optimal.append(candidate) return pareto_optimal
  Imports:
    - from typing import List, Dict, Any
    - from layers.layer_0_core.level_0 import filter_successful_results, worst_case_metric_sentinel [internal level_0]
  Line count: 80

### FILE: level_1/guards/__init__.py
  Module docstring: Invariant guard utilities.
  Imports:
    - from .arrays import check_array_finite
    - from .collections import check_min_collection_length
    - from .config import validate_config_section_exists, validate_feature_extraction_trainer_inputs
    - from .ensembles import validate_predictions_for_ensemble, validate_paired_predictions
    - from .none import check_not_none
    - from .result_checks import validate_execution_result
  Line count: 32
  __all__: ['check_array_finite', 'check_min_collection_length', 'validate_config_section_exists', 'validate_feature_extraction_trainer_inputs', 'validate_predictions_for_ensemble', 'validate_paired_predictions', 'check_not_none', 'validate_execution_result']

### FILE: level_1/guards/arrays.py
  Module docstring: NumPy array guards.
  Functions:
    - def check_array_finite(array: np.ndarray, *, name: str='array') -> None: """ Ensure array does not contain NaN or infinite values. Args: array: NumPy array to validate name: Name used in error message Raises: DataValidationError: If invalid values are found """ nan_mask = np.isnan(array) if nan_mask.any(): raise DataValidationError(f'{name} contains {nan_mask.sum()} NaN values') inf_mask = np.isinf(array) if inf_mask.any(): raise DataValidationError(f'{name} contains {inf_mask.sum()} infinite values')
  Imports:
    - import numpy as np
    - from layers.layer_0_core.level_0 import DataValidationError [internal level_0]
  Line count: 33

### FILE: level_1/guards/collections.py
  Module docstring: Collection length guards.
  Functions:
    - def check_min_collection_length(collection: Sized, min_length: int, *, name: str='collection') -> None: """ Ensure collection has at least a minimum length. Args: collection: Object implementing __len__ min_length: Required minimum length name: Name used in error message Raises: DataValidationError: If collection is too short """ actual_length = len(collection) if actual_length < min_length: raise DataValidationError(f'{name} has {actual_length} elements; minimum {min_length} required')
  Imports:
    - from typing import Sized
    - from layers.layer_0_core.level_0 import DataValidationError [internal level_0]
  Line count: 30

### FILE: level_1/guards/config.py
  Module docstring: Configuration structure guards.
  Functions:
    - def validate_config_section_exists(config: Any, section_name: str, *, config_name: str='config') -> None: """ Ensure a configuration object contains a non-None section. Args: config: Configuration object section_name: Attribute name to check config_name: Name used in error message Raises: ConfigValidationError: - If config is None - If section does not exist - If section value is None """ if config is None: raise ConfigValidationError(f'{config_name} cannot be None') if not hasattr(config, section_name): raise ConfigValidationError(f'{config_name}.{section_name} is missing') if getattr(config, section_name) is None: raise ConfigValidationError(f'{config_name}.{section_name} cannot be None')
    - def validate_feature_extraction_trainer_inputs(config: Any, device: Any, *, feature_extraction_mode_key: str='model.feature_extraction_mode') -> None: """ Validate config and device for feature extraction trainer. Args: config: Configuration object or dict. device: Must be torch.device. feature_extraction_mode_key: Config path for feature extraction flag. Raises: ConfigValidationError: If config is None or feature_extraction_mode is not True. TypeError: If device is not torch.device. """ torch_mod = get_torch() if config is None: raise ConfigValidationError('config cannot be None') if not get_config_value(config, feature_extraction_mode_key, default=False): raise ConfigValidationError('FeatureExtractionTrainer requires feature_extraction_mode=True') if not isinstance(device, torch_mod.device): raise TypeError(f'device must be torch.device, got {type(device)}')
  Imports:
    - from typing import Any
    - from layers.layer_0_core.level_0 import ConfigValidationError, get_config_value, get_torch [internal level_0]
  Line count: 68

### FILE: level_1/guards/ensembles.py
  Module docstring: Validation guards for ensemble prediction sets.
  Functions:
    - def validate_predictions_for_ensemble(predictions_list: List[np.ndarray], require_weights: bool=False, weights: Optional[List[float]]=None) -> Tuple[Tuple[int, ...], np.ndarray]: """ Validate a list of predictions for ensemble use, optionally with weights. Args: predictions_list: List of prediction arrays (one per model). require_weights: If True, weights must be provided and length-matched. weights: Optional list of per-model weights. Returns: Tuple of (common shape, stacked predictions array). Raises: ValueError: If validation fails or weights are required but absent/mismatched. """ validate_predictions_list(predictions_list) if require_weights: if weights is None: raise ValueError('weights are required for this ensemble method') if len(weights) != len(predictions_list): raise ValueError(f'Number of weights ({len(weights)}) must match number of predictions ({len(predictions_list)})') shape = validate_same_shape(predictions_list) stacked = np.stack(predictions_list, axis=0) return (shape, stacked)
    - def validate_paired_predictions(train_predictions: List[np.ndarray], val_predictions: List[np.ndarray]) -> int: """ Validate that train and validation prediction lists are compatible. Checks that both lists are non-empty, have the same number of models, and that the target dimensions match. Args: train_predictions: Per-model training predictions. val_predictions: Per-model validation predictions. Returns: Number of models (length of either list). Raises: ValueError: If lists are empty, unequal in length, or target dims differ. """ validate_predictions_list(train_predictions, 'train_predictions') validate_predictions_list(val_predictions, 'val_predictions') if len(train_predictions) != len(val_predictions): raise ValueError('Number of train and validation models must match') train_shape = train_predictions[0].shape val_shape = val_predictions[0].shape if train_shape[1:] != val_shape[1:]: raise ValueError(f'Train and val predictions must match on target dimensions. Train: {train_shape}, Val: {val_shape}') return len(train_predictions)
  Imports:
    - import numpy as np
    - from typing import List, Optional, Tuple
    - from layers.layer_0_core.level_0 import validate_predictions_list, validate_same_shape [internal level_0]
  Line count: 79

### FILE: level_1/guards/none.py
  Module docstring: None-value guard.
  Functions:
    - def check_not_none(value: Any, name: str='value') -> None: """ Ensure a value is not None. Args: value: Value to check name: Name used in error message Raises: DataValidationError: If value is None """ if value is None: raise DataValidationError(f'{name} cannot be None')
  Imports:
    - from typing import Any
    - from layers.layer_0_core.level_0 import DataValidationError [internal level_0]
  Line count: 20

### FILE: level_1/guards/result_checks.py
  Module docstring: Validate execution result and raise ExecutionError if failed.
  Functions:
    - def validate_execution_result(result: ExecutionResult, operation_name: str) -> None: """ Validate execution result and raise ExecutionError if failed. """ if result.succeeded: return error_msg = f'{operation_name} failed with return code {result.returncode}' if result.output: error_msg += '\n\nOutput:\n' + '\n'.join(result.output) if result.log_file: error_msg += f'\n\nFull output available in: {result.log_file}' raise ExecutionError(error_msg)
  Imports:
    - from layers.layer_0_core.level_0 import ExecutionError, ExecutionResult [internal level_0]
  Line count: 24

### FILE: level_1/io/__init__.py
  Module docstring: I/O utilities for submission files and generic TSV processing.
  Imports:
    - from .tsv_submission_formatter import TsvSubmissionFormatter
  Line count: 5
  __all__: ['TsvSubmissionFormatter']

### FILE: level_1/io/tsv_submission_formatter.py
  Module docstring: Generic TSV submission formatting, sorting, and limit enforcement.
  Classes:
    - TsvSubmissionFormatter
        Methods:
                 def __init__(self, parse_line: Optional[Callable[[str], Optional[Tuple[str, str, float, str]]]]=None, score_min: float=0.0, score_max: float=1.0): """ Args: parse_line: Optional custom parser. Default expects (id, term, score, line). score_min: Minimum valid score (inclusive) score_max: Maximum valid score (inclusive) """ self._score_min = score_min self._score_max = score_max self._parse_line = parse_line or self._default_parse_line
                 def _default_parse_line(self, line: str) -> Optional[Tuple[str, str, float, str]]: """Parse tab-separated: id, term, score.""" line = line.strip() if not line: return None parts = line.split('\t') if len(parts) >= 3: try: col0, col1, score = (parts[0], parts[1], float(parts[2])) if self._score_min < score <= self._score_max: return (col0, col1, score, line) except (ValueError, IndexError): pass return None
                 def parse_submission_line(self, line: str) -> Optional[Tuple[str, str, float, str]]: """Parse a single submission line.""" return self._parse_line(line)
                 def try_system_sort(self, input_path: Path, output_path: Path) -> bool: """Try system sort (Unix only). Returns True if succeeded.""" if sys.platform == 'win32': return False try: temp_dir = tempfile.gettempdir() with open(output_path, 'w', encoding='utf-8') as out: subprocess.run(['sort', '-t', '\t', '-k1,2', '-T', temp_dir, str(input_path)], stdout=out, stderr=subprocess.PIPE, text=True, check=True) logger.info(f'Sorted using system sort: {output_path}') return True except (subprocess.CalledProcessError, FileNotFoundError, OSError): return False
                 def sort_submission_external(self, input_path: str | Path, output_path: str | Path, chunk_size: int=1000000) -> None: """Sort TSV by first two columns. Uses system sort or chunked merge.""" input_path = Path(input_path) output_path = Path(output_path) if self.try_system_sort(input_path, output_path): return chunk_files = self._read_and_sort_chunks(input_path, chunk_size) self._merge_sorted_chunks(chunk_files, output_path) logger.info(f'External sort complete: {output_path}')
                 def _read_and_sort_chunks(self, input_path: Path, chunk_size: int) -> list[str]: """Read, sort in chunks, return temp file paths.""" chunk_files = [] chunk = [] with open(input_path, 'r', encoding='utf-8') as f: for line in f: parsed = self.parse_submission_line(line) if parsed: chunk.append(parsed) if len(chunk) >= chunk_size: chunk.sort(key=lambda x: (x[0], x[1])) tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tsv', encoding='utf-8') for _, _, _, orig in chunk: tf.write(orig + '\n') tf.close() chunk_files.append(tf.name) chunk = [] if chunk: chunk.sort(key=lambda x: (x[0], x[1])) tf = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tsv', encoding='utf-8') for _, _, _, orig in chunk: tf.write(orig + '\n') tf.close() chunk_files.append(tf.name) return chunk_files
                 def _merge_sorted_chunks(self, chunk_files: list[str], output_path: Path) -> None: """Merge sorted chunks with heap.""" with open(output_path, 'w', encoding='utf-8') as out_file: handles = [open(f, 'r', encoding='utf-8') for f in chunk_files] iters = [iter(h) for h in handles] heap = [] for i, it in enumerate(iters): try: line = next(it).strip() if line: parts = line.split('\t') if len(parts) >= 2: heap.append((parts[0], parts[1], i, line)) except StopIteration: pass heapq.heapify(heap) while heap: _, _, idx, line = heapq.heappop(heap) out_file.write(line + '\n') try: next_line = next(iters[idx]).strip() if next_line: parts = next_line.split('\t') if len(parts) >= 2: heapq.heappush(heap, (parts[0], parts[1], idx, next_line)) except StopIteration: pass for h in handles: h.close() for f in chunk_files: try: Path(f).unlink() except Exception: pass
                 def enforce_prediction_limits(self, submission_path: str | Path, max_predictions_per_id: int=1500, output_path: Optional[str | Path]=None) -> str: """ Keep top-K predictions per first column (e.g. protein_id). Returns: Path to output file. """ submission_path = Path(submission_path) output_path = output_path or str(submission_path.with_suffix('')) + '_limited.tsv' output_path = Path(output_path) id_predictions: dict[str, list[Tuple[float, str]]] = defaultdict(list) with open(submission_path, 'r', encoding='utf-8') as f: for line in f: parsed = self.parse_submission_line(line) if parsed: id_val, term, score, _ = parsed if len(id_predictions[id_val]) < max_predictions_per_id: heapq.heappush(id_predictions[id_val], (score, term)) else: min_score, _ = id_predictions[id_val][0] if score > min_score: heapq.heapreplace(id_predictions[id_val], (score, term)) final_count = 0 with open(output_path, 'w', encoding='utf-8') as out: for id_val, preds in id_predictions.items(): for score, term in sorted(preds, reverse=True): out.write(f'{id_val}\t{term}\t{score:.6f}\n') final_count += 1 logger.info(f'Enforced limit: {final_count:,} predictions') return str(output_path)
  Imports:
    - import heapq
    - import subprocess
    - import sys
    - import tempfile
    - from collections import defaultdict
    - from pathlib import Path
    - from typing import Callable, Optional, Tuple
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 198

### FILE: level_1/ontology/__init__.py
  Module docstring: Ontology utilities.
  Imports:
    - from .config_resolver import OntologyConfigResolver
    - from .hierarchy_propagator import HierarchyPropagator
  Line count: 6
  __all__: ['HierarchyPropagator', 'OntologyConfigResolver']

### FILE: level_1/ontology/config_resolver.py
  Module docstring: Generic per-ontology config resolution for multi-ontology contests.
  Classes:
    - OntologyConfigResolver
        Methods:
                 def get_ontology_config(self, ontology: str, base_config: Any) -> Dict[str, Any]: """ Get configuration for a specific ontology. Merges base config with per-ontology overrides from base_config.per_ontology_hyperparams if present. Args: ontology: Ontology code (e.g. 'F', 'P', 'C') base_config: Base configuration object Returns: Configuration dict with ontology-specific values merged in """ base_dict = base_config.__dict__.copy() if hasattr(base_config, '__dict__') else {} if hasattr(base_config, 'per_ontology_hyperparams'): per_ontology = getattr(base_config, 'per_ontology_hyperparams', {}) ont_hyperparams = per_ontology.get(ontology, {}) base_dict.update(ont_hyperparams) return base_dict
  Imports:
    - from typing import Any, Dict
  Line count: 39

### FILE: level_1/ontology/hierarchy_propagator.py
  Module docstring: Generic hierarchy propagation for ontology graphs.
  Classes:
    - HierarchyPropagator
        Methods:
                 def __init__(self, parents_map: Dict[str, Set[str]] | None=None, children_map: Dict[str, Set[str]] | None=None, term_to_idx: Dict[str, int] | None=None): """ Initialize with parent/child maps. Args: parents_map: term_id -> set of parent term_ids children_map: term_id -> set of child term_ids (built from parents_map if None) term_to_idx: Optional mapping of term_id -> column index for propagation """ self._parents_map = parents_map or {} self._children_map = children_map or (_build_children_from_parents(self._parents_map) if self._parents_map else {}) self._ancestors_cache: Dict[str, Set[str]] = {} self._descendants_cache: Dict[str, Set[str]] = {} self.parents_map = self._parents_map self.term_to_idx = term_to_idx or {}
                 def load_from_obo(self, obo_path: Path) -> None: """Load hierarchy from OBO file.""" self._parents_map, self._children_map = parse_obo_file(obo_path) self.parents_map = self._parents_map self._ancestors_cache = {} self._descendants_cache = {}
                 def parse_obo(self, obo_path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]: """Parse OBO file and set internal state. Returns (parents_map, children_map).""" self._parents_map, self._children_map = parse_obo_file(obo_path) self.parents_map = self._parents_map self._ancestors_cache = {} self._descendants_cache = {} return (self._parents_map, self._children_map)
                 def set_hierarchy(self, parents_map: Dict[str, Set[str]], term_to_idx: Dict[str, int]) -> None: """Set hierarchy from parent map and term-to-index mapping.""" self.parents_map = parents_map self.term_to_idx = term_to_idx children_map = _build_children_from_parents(parents_map) self.set_from_dicts(parents_map, children_map)
                 def set_from_dicts(self, parents_map: Dict[str, Set[str]], children_map: Dict[str, Set[str]]) -> None: """Set hierarchy from pre-parsed maps.""" self._parents_map = parents_map self._children_map = children_map self.parents_map = parents_map self._ancestors_cache = {} self._descendants_cache = {}
                 def get_ancestors(self, node_id: str) -> Set[str]: """Get all ancestor nodes (transitive closure).""" if node_id in self._ancestors_cache: return self._ancestors_cache[node_id] ancestors: Set[str] = set() stack = [node_id] while stack: current = stack.pop() for parent in self._parents_map.get(current, set()): if parent not in ancestors: ancestors.add(parent) stack.append(parent) self._ancestors_cache[node_id] = ancestors return ancestors
                 def get_descendants(self, node_id: str) -> Set[str]: """Get all descendant nodes (transitive closure).""" if node_id in self._descendants_cache: return self._descendants_cache[node_id] descendants: Set[str] = set() stack = [node_id] while stack: current = stack.pop() for child in self._children_map.get(current, set()): if child not in descendants: descendants.add(child) stack.append(child) self._descendants_cache[node_id] = descendants return descendants
                 def get_parents(self, node_id: str) -> Set[str]: """Get direct parent nodes.""" return self._parents_map.get(node_id, set())
                 def get_children(self, node_id: str) -> Set[str]: """Get direct child nodes.""" return self._children_map.get(node_id, set())
                 def propagate_predictions_batch(self, predictions: np.ndarray, term_ids: List[str], iterations: int=3) -> np.ndarray: """ Propagate predictions up the hierarchy using max operation. Child scores propagate to ancestors; parent gets max of its score and all descendant scores. Args: predictions: (n_samples, n_terms) probability matrix term_ids: List of term IDs corresponding to columns iterations: Number of propagation passes Returns: Propagated predictions (n_samples, n_terms) """ if not term_ids or len(term_ids) != predictions.shape[1]: raise ValueError(f'term_ids length ({len(term_ids)}) must match predictions columns ({predictions.shape[1]})') term_to_idx = {term: idx for idx, term in enumerate(term_ids)} propagated = predictions.copy() for _ in range(iterations): for term_idx, term_id in enumerate(term_ids): ancestors = self.get_ancestors(term_id) for ancestor_id in ancestors: ancestor_idx = term_to_idx.get(ancestor_id) if ancestor_idx is not None: propagated[:, ancestor_idx] = np.maximum(propagated[:, ancestor_idx], predictions[:, term_idx]) predictions = propagated.copy() return propagated
  Functions:
    - def _build_children_from_parents(parents_map: Dict[str, Set[str]]) -> Dict[str, Set[str]]: """Build children map from parents map.""" from collections import defaultdict children: Dict[str, Set[str]] = defaultdict(set) for child, parents in parents_map.items(): for parent in parents: children[parent].add(child) return dict(children)
  Imports:
    - import numpy as np
    - from pathlib import Path
    - from typing import Dict, List, Set, Tuple
    - from layers.layer_0_core.level_0 import parse_obo_file [internal level_0]
  Line count: 167

### FILE: level_1/pipelines/__init__.py
  Module docstring: Reusable orchestration shells for PipelineResult workflows.
  Imports:
    - from .orchestration import merge_pipeline_results_ok, run_pipeline_result_with_validation_first, run_two_stage_pipeline_result_with_validation_first
    - from .pipeline_shells import BasePipeline, ValidateFirstRunner, ValidateFirstPipelineResultShell, TwoStageValidateFirstPipelineResultShell
  Line count: 24
  __all__: ['merge_pipeline_results_ok', 'run_pipeline_result_with_validation_first', 'run_two_stage_pipeline_result_with_validation_first', 'BasePipeline', 'ValidateFirstRunner', 'ValidateFirstPipelineResultShell', 'TwoStageValidateFirstPipelineResultShell']

### FILE: level_1/pipelines/orchestration.py
  Module docstring: Reusable validate-then-run patterns for PipelineResult workflows.
  Functions:
    - def run_pipeline_result_with_validation_first(*, stage: str, data_root: str, max_targets: int, run_ctx: Optional[Any], validate_first: bool, validate_fn: Callable[..., PipelineResult], on_success: Callable[[], PipelineResult]) -> PipelineResult: """If validate_first, run validate_fn; on success call on_success and return its PipelineResult.""" if validate_first: validation = validate_fn(data_root=data_root, max_targets=max_targets, run_ctx=run_ctx) if not validation.success: return PipelineResult.fail(stage=str(stage), error=validation.error or 'Validation failed', metadata={'blocked_by': 'validate_data', **dict(validation.metadata)}) try: result = on_success() if isinstance(result, PipelineResult): return result return PipelineResult.fail(stage=str(stage), error='Pipeline returned unexpected result type', metadata={'blocked_by': None}) except Exception as e: return PipelineResult.fail(stage=str(stage), error=str(e), metadata={'error_repr': repr(e)})
    - def merge_pipeline_results_ok(*, stage: str, a: PipelineResult, b: PipelineResult) -> PipelineResult: """Combine two successful results (artifacts + metadata); both should be success.""" meta_a = dict(a.metadata) if a.metadata else {} meta_b = dict(b.metadata) if b.metadata else {} return PipelineResult.ok(stage=str(stage), artifacts={**dict(a.artifacts), **dict(b.artifacts)}, metadata={**meta_a, **meta_b})
    - def run_two_stage_pipeline_result_with_validation_first(*, stage: str, data_root: str, max_targets: int, run_ctx: Optional[Any], validate_first: bool, validate_fn: Callable[..., PipelineResult], first_stage: str, first_fn: Callable[[], PipelineResult], second_stage: str, second_fn: Callable[[PipelineResult], PipelineResult]) -> PipelineResult: """ Run a two-stage PipelineResult workflow with an optional shared validation step. """ def _on_success() -> PipelineResult: first = first_fn() if not isinstance(first, PipelineResult): return PipelineResult.fail(stage=str(first_stage), error='First stage returned unexpected result type') if not first.success: return first second = second_fn(first) if not isinstance(second, PipelineResult): return PipelineResult.fail(stage=str(second_stage), error='Second stage returned unexpected result type') if not second.success: return second return merge_pipeline_results_ok(stage=str(stage), a=first, b=second) return run_pipeline_result_with_validation_first(stage=str(stage), data_root=str(data_root), max_targets=int(max_targets), run_ctx=run_ctx, validate_first=bool(validate_first), validate_fn=validate_fn, on_success=_on_success)
  Imports:
    - from typing import Any, Callable, Optional
    - from level_0 import PipelineResult [internal level_0]
  Line count: 93

### FILE: level_1/pipelines/pipeline_shells.py
  Module docstring: Small, reusable orchestration shells for PipelineResult pipelines.
  Classes:
    - BasePipeline
        Methods:
                 def run(self) -> T: raise NotImplementedError
    - ValidateFirstRunner
        Methods:
                 def run(self) -> T: self.validate_fn(data_root=self.data_root, max_targets=int(self.max_targets or 0)) return self.run_fn()
    - ValidateFirstPipelineResultShell
        Methods:
                 def run(self) -> PipelineResult: return self.runner_fn(stage=str(self.stage), data_root=str(self.data_root), max_targets=int(self.max_targets), run_ctx=self.run_ctx, validate_first=bool(self.validate_first), validate_fn=self.validate_fn, on_success=self.on_success)
    - TwoStageValidateFirstPipelineResultShell
        Methods:
                 def run(self) -> PipelineResult: return self.runner_fn(stage=str(self.stage), data_root=str(self.data_root), max_targets=int(self.max_targets), run_ctx=self.run_ctx, validate_first=bool(self.validate_first), validate_fn=self.validate_fn, first_stage=str(self.first_stage), first_fn=self.first_fn, second_stage=str(self.second_stage), second_fn=self.second_fn)
  Imports:
    - from dataclasses import dataclass
    - from typing import Any, Callable, Generic, Optional, TypeVar
    - from level_0 import PipelineResult [internal level_0]
  Line count: 93

### FILE: level_1/protein/__init__.py
  Module docstring: Protein utilities.
  Imports:
    - from .id_utils import normalize_protein_id, normalize_protein_ids, find_common_protein_ids, align_embeddings_to_common_ids
  Line count: 15
  __all__: ['normalize_protein_id', 'normalize_protein_ids', 'find_common_protein_ids', 'align_embeddings_to_common_ids']

### FILE: level_1/protein/id_utils.py
  Module docstring: Protein ID normalization and embedding alignment utilities.
  Functions:
    - def normalize_protein_id(protein_id: Union[str, int, float]) -> str: """ Normalize protein ID to standard format. Handles UniProt format: sp|Q8VY15|NAME -> Q8VY15 Args: protein_id: Protein ID in various formats Returns: Normalized protein ID (accession as string) """ if not protein_id: return str(protein_id) if protein_id is not None else '' protein_id = str(protein_id) if '|' in protein_id: parts = protein_id.split('|') if len(parts) >= 2: return parts[1] return protein_id
    - def normalize_protein_ids(protein_ids: List[Union[str, int, float]]) -> List[str]: """Normalize a list of protein IDs.""" return [normalize_protein_id(pid) for pid in protein_ids]
    - def find_common_protein_ids(embedding_list: List[Tuple[np.ndarray, List[str]]], target_ids: List[str]) -> List[str]: """ Find common protein IDs across embeddings and target IDs. Args: embedding_list: List of (embedding_array, id_list) tuples target_ids: Target protein IDs to align to Returns: List of common protein IDs (normalized), preserving target order """ id_sets = [] for _, embed_ids in embedding_list: normalized_ids = {normalize_protein_id(str(pid)) for pid in embed_ids} id_sets.append(normalized_ids) if id_sets: embedding_intersection = set.intersection(*id_sets) if len(id_sets) > 1 else id_sets[0] logger.debug(f'Intersection of {len(id_sets)} embedding types: {len(embedding_intersection):,} proteins') target_id_set = {normalize_protein_id(str(pid)) for pid in target_ids} logger.debug(f'Target IDs: {len(target_id_set):,} proteins') all_id_sets = id_sets + [target_id_set] common_id_set = set.intersection(*all_id_sets) normalized_target_ids = [normalize_protein_id(str(pid)) for pid in target_ids] common_ids = [pid for pid in normalized_target_ids if pid in common_id_set] logger.info(f'Found {len(common_ids):,} common proteins across {len(id_sets)} embedding types and {len(target_ids):,} target IDs') if len(common_ids) == 0: logger.warning('No common IDs found across embeddings and target_ids') if len(embedding_intersection) > 0: overlap = embedding_intersection & target_id_set logger.warning(f'Overlap between embedding IDs and target IDs: {len(overlap):,} proteins') return common_ids return [normalize_protein_id(str(pid)) for pid in target_ids]
    - def align_embeddings_to_common_ids(embedding_list: List[Tuple[np.ndarray, List[str]]], common_ids: List[str]) -> List[np.ndarray]: """ Align each embedding array to common protein IDs. Missing proteins get zero vectors. Args: embedding_list: List of (embedding_array, id_list) tuples common_ids: Common protein IDs to align to Returns: List of aligned embedding arrays """ aligned_embeddings = [] for embeds, embed_ids in embedding_list: normalized_embed_ids = [normalize_protein_id(str(pid)) for pid in embed_ids] embed_dict = dict(zip(normalized_embed_ids, embeds)) aligned = [] for norm_pid in common_ids: if norm_pid in embed_dict: aligned.append(embed_dict[norm_pid]) else: aligned.append(np.zeros(embeds.shape[1], dtype=embeds.dtype)) aligned_embeddings.append(np.array(aligned)) return aligned_embeddings
  Imports:
    - import numpy as np
    - from typing import List, Tuple, Union
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 114

### FILE: level_1/runtime/__init__.py
  Module docstring: Runtime-level utilities.
  Imports:
    - from . import config, cuda
    - from .config import *
    - from .cuda import *
    - from .base_pipeline import BasePipeline
    - from .chunked_prediction import predict_in_chunks, predict_proteins_in_chunks
    - from .device import is_cuda_available, get_device_info, get_device
    - from .lazy_imports import lazy_import
    - from .metadata_paths import find_metadata_candidates
    - from .notebook_runner import safe_execute_cell
    - from .paths import get_environment_type, get_environment_paths, get_environment_root, get_default_submission_csv_path, get_kaggle_working_submission_csv_path, resolve_environment_path, resolve_path
    - from .process import run_command
    - from .progress_config import ProgressVerbosity, ProgressConfig
    - from .seed import set_seed
  Line count: 67

### FILE: level_1/runtime/base_pipeline.py
  Module docstring: Base pipeline abstract class.
  Classes:
    - BasePipeline
        Methods:
                 def __init__(self, config: Any) -> None: """ Initialize pipeline. Args: config: Configuration object (domain-specific config). """ self.config = config self.results: Optional[Dict[str, Any]] = None
                 @abstractmethod def setup(self) -> None: """ Setup pipeline: validate inputs, create directories, initialize components. This method should: - Validate configuration - Create output directories - Initialize required components - Check prerequisites Raises: ValueError: If configuration is invalid. FileNotFoundError: If required files don't exist. """ ...
                 @abstractmethod def execute(self) -> Dict[str, Any]: """ Execute the pipeline. This is the main pipeline logic. Should return a dictionary with results (metrics, paths, etc.). Returns: Dictionary with pipeline results. Should include: - 'success': bool - 'metrics': dict (optional) - 'output_paths': dict (optional) - 'metadata': dict (optional) Raises: RuntimeError: If pipeline execution fails. """ ...
                 def cleanup(self) -> None: """ Cleanup pipeline resources. This method is called after execute() to clean up any resources (close files, release memory, etc.). Override if needed. """ pass
                 def run(self) -> Dict[str, Any]: """ Run the complete pipeline lifecycle. Returns: Pipeline results dictionary. """ try: logger.info('🚀 Starting pipeline: %s', self.__class__.__name__) self.setup() self.results = self.execute() self.cleanup() logger.info('✅ Pipeline completed: %s', self.__class__.__name__) return self.results except Exception as e: logger.error('❌ Pipeline failed: %s', self.__class__.__name__) logger.error(' Error: %s', str(e)) raise
  Imports:
    - from abc import ABC, abstractmethod
    - from typing import Any, Dict, Optional
    - from level_0 import get_logger [internal level_0]
  Line count: 98

### FILE: level_1/runtime/chunked_prediction.py
  Module docstring: Chunked model prediction for memory-efficient inference on large datasets.
  Functions:
    - def _dispatch_predict(model, X: np.ndarray) -> np.ndarray: """Dispatch prediction to predict_proba or predict depending on model interface.""" if hasattr(model, 'predict_proba'): return model.predict_proba(X) if hasattr(model, 'predict'): return model.predict(X) raise ValueError('Model must have predict_proba() or predict() method')
    - def predict_in_chunks(model, X: np.ndarray, batch_size: int=1000, progress_interval: int=100) -> np.ndarray: """ Make predictions in chunks for memory efficiency. Processes predictions in batches to avoid OOM on large test sets. Args: model: Trained model with predict_proba or predict method. X: Feature matrix of shape (n_samples, n_features). batch_size: Number of samples per prediction batch (default: 1000). progress_interval: Log progress every N batches (default: 100). Returns: Predictions array of shape (n_samples, n_targets). """ n_samples = len(X) total_batches = (n_samples + batch_size - 1) // batch_size predictions_list = [] logger.info(f'Making predictions in chunks (batch_size={batch_size:,}, total_samples={n_samples:,})...') for i in range(0, n_samples, batch_size): batch_num = i // batch_size + 1 batch_preds = _dispatch_predict(model, X[i:i + batch_size]) predictions_list.append(batch_preds) if batch_num % progress_interval == 0 or batch_num == total_batches: logger.info(f' Processed {min(i + batch_size, n_samples):,}/{n_samples:,} samples ({batch_num}/{total_batches} batches)') predictions = np.vstack(predictions_list) logger.info(f'✓ Completed predictions: shape {predictions.shape}') return predictions
    - def predict_proteins_in_chunks(model, protein_ids: List[str], feature_extractor: Callable, batch_size: int=3000, output_file: Optional[str]=None, format_prediction_row: Optional[Callable]=None, progress_interval: int=10) -> Optional[np.ndarray]: """ Make predictions for proteins in chunks (protein-level batching). Processes proteins in batches to prevent OOM on large test sets: 1. Extracts features for the batch via the injected feature_extractor. 2. Makes predictions for the batch. 3. Writes to file immediately (if output_file provided), then deletes the prediction matrix to free memory. Args: model: Trained model with predict_proba or predict method. protein_ids: List of protein IDs to predict for. feature_extractor: Callable(protein_ids) -> (features, aligned_ids). batch_size: Number of proteins per batch (default: 3000). output_file: Optional path to write predictions incrementally. If provided, the caller must also supply format_prediction_row. Returns None when this is set. format_prediction_row: Callable(protein_id, prediction_row) -> str. Required when output_file is provided. Formats a single protein's predictions as a line to write. progress_interval: Log progress every N batches (default: 10). Returns: Predictions array of shape (n_proteins, n_targets) if output_file is None. Returns None if output_file is provided (predictions written to disk incrementally). Raises: ValueError: If output_file is provided but format_prediction_row is not. """ if output_file is not None and format_prediction_row is None: raise ValueError('format_prediction_row is required when output_file is provided') n_proteins = len(protein_ids) total_batches = (n_proteins + batch_size - 1) // batch_size logger.info(f'Making protein-level predictions in chunks (batch_size={batch_size:,}, total_proteins={n_proteins:,})...') all_predictions: Optional[List[np.ndarray]] = [] if output_file is None else None output_handle = None if output_file: output_handle = open(output_file, 'w') logger.info(f'Writing predictions incrementally to {output_file}') try: for batch_idx in range(0, n_proteins, batch_size): batch_protein_ids = protein_ids[batch_idx:batch_idx + batch_size] batch_num = batch_idx // batch_size + 1 batch_features, aligned_ids = feature_extractor(batch_protein_ids) batch_preds = _dispatch_predict(model, batch_features) if output_handle is not None: for i, protein_id in enumerate(aligned_ids): output_handle.write(format_prediction_row(protein_id, batch_preds[i])) del batch_preds gc.collect() else: all_predictions.append(batch_preds) del batch_features if batch_num % progress_interval == 0 or batch_num == total_batches: logger.info(f' Processed {min(batch_idx + batch_size, n_proteins):,}/{n_proteins:,} proteins ({batch_num}/{total_batches} batches)') if output_handle: logger.info(f'✓ Completed predictions: {n_proteins:,} proteins written to {output_file}') return None predictions = np.vstack(all_predictions) logger.info(f'✓ Completed predictions: shape {predictions.shape}') return predictions finally: if output_handle: output_handle.close()
  Imports:
    - import gc
    - import numpy as np
    - from typing import Callable, List, Optional
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 165

### FILE: level_1/runtime/config/__init__.py
  Module docstring: Configuration classes for runtime.
  Imports:
    - from .config_creation import create_config
    - from .config_sections import format_config_section, log_config_section, print_config_section
    - from .evaluation import EvaluationConfig
    - from .grid_search import GridSearchConfig
    - from .training import TrainingConfig
  Line count: 21
  __all__: ['create_config', 'format_config_section', 'log_config_section', 'print_config_section', 'EvaluationConfig', 'GridSearchConfig', 'TrainingConfig']

### FILE: level_1/runtime/config/config_creation.py
  Module docstring: Config creation utilities for CLI.
  Functions:
    - def create_config(contest_name: str, args: argparse.Namespace, get_contest: Callable[[str], Any], get_vision_config_builder: Optional[Callable[..., Any]]=None, get_tabular_config_builder: Optional[Callable[..., Any]]=None) -> Any: """ Create configuration object for the contest. Orchestration does not import contest, vision, or tabular; caller provides get_contest and, per model type, get_vision_config_builder / get_tabular_config_builder. Args: contest_name: Contest name. args: Parsed arguments. get_contest: Callable that takes contest name and returns contest dict (paths, config, data_schema, etc.). Provided by contest layer. get_vision_config_builder: Optional. For model_type=='vision', callable (contest_name, args, data_root, output_dir, data_schema) -> config. Provided by scripts layer so orchestration does not import vision. get_tabular_config_builder: Optional. For model_type=='tabular', callable (contest_name, args, data_root, output_dir, data_schema) -> config. Provided by scripts layer so orchestration does not import tabular. Returns: Configuration object (VisionConfig or TabularConfig). """ contest = get_contest(contest_name) contest_paths = contest['paths']() data_schema = contest.get('data_schema') model_type = get_arg(args, 'model_type', 'vision') data_root = get_arg(args, 'data_root') or str(contest_paths.local_data_root) output_dir = get_arg(args, 'output_dir', 'output') if model_type == 'vision': if get_vision_config_builder is None: raise ConfigValidationError('Vision config requires get_vision_config_builder from scripts layer (orchestration does not import vision).') return get_vision_config_builder(contest_name, args, data_root, output_dir, data_schema) else: if get_tabular_config_builder is None: raise ConfigValidationError('Tabular config requires get_tabular_config_builder from scripts layer (orchestration does not import tabular).') return get_tabular_config_builder(contest_name, args, data_root, output_dir, data_schema)
  Imports:
    - import argparse
    - from typing import Optional, Callable, Any
    - from layers.layer_0_core.level_0 import get_arg, ConfigValidationError [internal level_0]
  Line count: 61

### FILE: level_1/runtime/config/config_sections.py
  Module docstring: Configuration section formatting utilities.
  Functions:
    - def format_config_section(title: str, config: Mapping[str, Any], width: int=60) -> str: """ Format a configuration section with a title and a separator. Args: title: Section title config: Dictionary of configuration key-value pairs to display None values are skipped """ lines = [] separator = '=' * width lines.append(separator) lines.append(title) lines.append(separator) for key, value in config.items(): if value is not None: lines.append(f' {key}: {value}') lines.append(separator) return '\n'.join(lines)
    - def log_config_section(title: str, config: Mapping[str, Any]) -> None: """ Log a formatted configuration section with consistent header formatting. Args: title: Section title config: Dictionary of configuration key-value pairs to display None values are skipped """ logger.info(format_config_section(title, config))
    - def print_config_section(title: str, config: Mapping[str, Any], width: int=60) -> None: """ Print a formatted configuration section to stdout. Args: title: Section title config: Dictionary of configuration key-value pairs to display None values are skipped width: Separator width """ print(format_config_section(title, config, width))
  Imports:
    - from typing import Any, Mapping
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 60

### FILE: level_1/runtime/config/evaluation.py
  Module docstring: Evaluation configuration.
  Classes:
    - EvaluationConfig
        Methods:
                 def __post_init__(self): if self.additional_metrics is None: self.additional_metrics = []
  Imports:
    - from dataclasses import dataclass
    - from typing import List, Optional, Literal
    - from layers.layer_0_core.level_0 import RuntimeConfig [internal level_0]
  Line count: 27

### FILE: level_1/runtime/config/grid_search.py
  Module docstring: Shared configuration for grid search modes.
  Classes:
    - GridSearchConfig
  Imports:
    - from dataclasses import dataclass
    - from layers.layer_0_core.level_0 import RuntimeConfig [internal level_0]
  Line count: 35

### FILE: level_1/runtime/config/training.py
  Module docstring: Generic training configuration.
  Classes:
    - TrainingConfig
  Imports:
    - from dataclasses import dataclass
    - from typing import Literal, Optional
    - from layers.layer_0_core.level_0 import RuntimeConfig, TrainingSchema [internal level_0]
  Line count: 45

### FILE: level_1/runtime/cuda/__init__.py
  Module docstring: Memory management utilities.
  Imports:
    - from .gpu_cleanup import cleanup_gpu_memory, perform_aggressive_cleanup
    - from .memory import get_model_memory_usage, estimate_memory_mb, get_available_memory_mb, get_total_memory_mb, get_memory_usage_percent
    - from .monitoring import print_gpu_memory_status
  Line count: 31
  __all__: ['cleanup_gpu_memory', 'perform_aggressive_cleanup', 'get_model_memory_usage', 'estimate_memory_mb', 'get_available_memory_mb', 'get_total_memory_mb', 'get_memory_usage_percent', 'print_gpu_memory_status']

### FILE: level_1/runtime/cuda/gpu_cleanup.py
  Module docstring: Memory cleanup utilities.
  Functions:
    - def cleanup_gpu_memory() -> None: """ Clean up GPU memory after training or inference. Essential for sequential training of multiple models on limited GPU memory. Also cleans up any pre-loaded data tensors. Lessons learned from Kaggle ML Competition: - Centralized GPU cleanup logic eliminates duplication - Should be called after each model training/inference - Clears CUDA cache and synchronizes before garbage collection """ if torch is None or not torch.cuda.is_available(): gc.collect() return try: torch.cuda.empty_cache() torch.cuda.synchronize() gc.collect() torch.cuda.empty_cache() except Exception: gc.collect()
    - def perform_aggressive_cleanup() -> None: """ Perform aggressive GPU memory cleanup. Includes resetting memory statistics and multiple cleanup passes for thorough memory release, useful for OOM recovery. """ if torch is None or not torch.cuda.is_available(): return try: torch.cuda.reset_peak_memory_stats() except RuntimeError as e: raise RuntimeError('Could not reset peak memory stats:') from e for _ in range(5): gc.collect() if torch is not None: try: torch.cuda.empty_cache() torch.cuda.synchronize() except RuntimeError: pass if torch is not None: try: gc.collect() torch.cuda.empty_cache() except RuntimeError: pass
  Imports:
    - import gc
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal level_0]
  Line count: 72

### FILE: level_1/runtime/cuda/memory.py
  Module docstring: Memory management utilities - pure runtime facts.
  Functions:
    - def get_model_memory_usage() -> Optional[float]: """ Get approximate GPU memory usage in MB. Returns: Memory usage in MB, or None if CUDA unavailable Example: >>> mem = get_model_memory_usage() >>> if mem and mem > 1000: ... print("High memory usage detected") """ torch = get_torch() if not is_torch_available() or not torch.cuda.is_available(): return None try: return torch.cuda.memory_allocated() / 1024 ** 2 except Exception: return None
    - def estimate_memory_mb(array: np.ndarray) -> float: """ Estimate memory usage of a numpy array in MB. Args: array: Numpy array Returns: Estimated memory in megabytes Example: >>> arr = np.zeros((1000, 1000)) >>> mem = estimate_memory_mb(arr) >>> print(f"Array uses {mem:.2f} MB") """ return array.nbytes / 1024 ** 2
    - def get_available_memory_mb() -> float: """ Get available system memory in MB. Returns: Available memory in megabytes Example: >>> free_mem = get_available_memory_mb() >>> if free_mem < 1000: ... print("Low memory warning!") """ return psutil.virtual_memory().available / 1024 ** 2
    - def get_total_memory_mb() -> float: """ Get total system memory in MB. Returns: Total memory in megabytes """ return psutil.virtual_memory().total / 1024 ** 2
    - def get_memory_usage_percent() -> float: """ Get current memory usage as percentage. Returns: Memory usage percentage (0-100) """ return psutil.virtual_memory().percent
  Imports:
    - import psutil
    - import numpy as np
    - from typing import Optional
    - from layers.layer_0_core.level_0 import get_torch, is_torch_available [internal level_0]
  Line count: 89

### FILE: level_1/runtime/cuda/monitoring.py
  Module docstring: Memory monitoring utilities.
  Functions:
    - def print_gpu_memory_status() -> None: """ Log GPU memory status if available. Gracefully handles missing torch or CUDA. Only logs in Kaggle environment. """ try: torch = get_torch() if torch.cuda.is_available(): BYTES_PER_GB = 1024 * 1024 * 1024 allocated = torch.cuda.memory_allocated() / BYTES_PER_GB reserved = torch.cuda.memory_reserved() / BYTES_PER_GB logger.info(f'📊 GPU Memory Status (before grid search):') logger.info(f' Allocated: {allocated:.2f} GB') logger.info(f' Reserved: {reserved:.2f} GB') except ImportError: pass except (RuntimeError, AttributeError) as e: raise RuntimeError('Could not check GPU memory status:') from e except Exception as e: raise RuntimeError('Unexpected error checking GPU memory:') from e
  Imports:
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal level_0]
  Line count: 31

### FILE: level_1/runtime/device.py
  Module docstring: Hardware and device detection utilities.
  Functions:
    - def is_cuda_available() -> bool: """Return True if CUDA is available.""" torch = get_torch() if torch is None: return False return bool(torch.cuda.is_available())
    - def get_device_info() -> Dict[str, object]: """ Return hardware information. Returns: { "cuda_available": bool, "device_count": int, "device_names": List[str], } """ torch = get_torch() if torch is None or not torch.cuda.is_available(): return {'cuda_available': False, 'device_count': 0, 'device_names': []} count = torch.cuda.device_count() names: List[str] = [torch.cuda.get_device_name(i) for i in range(count)] return {'cuda_available': True, 'device_count': count, 'device_names': names}
    - def get_device(device: str='auto') -> str: """ Resolve device identifier. Always returns a string identifier: "cpu" "cuda" "cuda:0" Never returns torch.device (core should not leak torch objects). """ if not isinstance(device, str): raise DeviceError(f'device must be str, got {type(device).__name__}') if not device or not device.strip(): raise DeviceError('device cannot be empty') device = device.strip().lower() valid_prefixes = ('auto', 'cpu', 'cuda') if not any((device.startswith(p) for p in valid_prefixes)): raise DeviceError(f"Invalid device '{device}'. Must be one of: 'auto', 'cpu', 'cuda', 'cuda:0', etc.") torch = get_torch() if device == 'auto': if torch and torch.cuda.is_available(): return 'cuda' return 'cpu' if device.startswith('cuda'): if torch is None or not torch.cuda.is_available(): return 'cpu' return device return 'cpu'
  Imports:
    - from typing import Dict, List
    - from layers.layer_0_core.level_0 import get_torch, DeviceError [internal level_0]
  Line count: 87

### FILE: level_1/runtime/lazy_imports.py
  Module docstring: Lazy imports logic.
  Functions:
    - def lazy_import(module: str, attrs: Union[str, Iterable[str]], *, package: str, warn: str) -> Union[Any, Tuple[Any, ...], None]: """ Generic lazy importer. """ if isinstance(attrs, str): attrs = (attrs,) single = True else: single = False try: mod = __import__(module, fromlist=list(attrs)) values = tuple((getattr(mod, a) for a in attrs)) return values[0] if single else values except Exception: logger.warning('%s not available. %s', package, warn) if single: return None return tuple((None for _ in attrs))
  Imports:
    - from typing import Iterable, Union, Tuple, Any
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 38

### FILE: level_1/runtime/metadata_paths.py
  Module docstring: Metadata path resolution utilities.
  Functions:
    - def find_metadata_candidates(model_path: Path) -> list[Path]: """ Find candidate paths for model metadata file. Args: model_path: Model path (file or directory) Returns: List of candidate metadata file paths """ metadata_candidates = [] if model_path.is_dir(): metadata_candidates.append(model_path / 'model_metadata.json') metadata_candidates.append(model_path.parent / 'model_metadata.json') else: metadata_candidates.append(model_path.parent / 'model_metadata.json') metadata_candidates.append(model_path.parent.parent / 'model_metadata.json') return metadata_candidates
  Imports:
    - from pathlib import Path
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 31

### FILE: level_1/runtime/notebook_runner.py
  Module docstring: Runs a notebook cell safely if enabled.
  Functions:
    - def safe_execute_cell(cell_id: str, enabled_cells: Mapping[str, bool], operation: Callable[[], None]) -> None: """ Safely execute a notebook cell if enabled. Wraps execution errors in ExecutionError with cell context. """ if not enabled_cells.get(cell_id, False): logger.info(f'Cell {cell_id} skipped.') return try: operation() except Exception as exc: raise ExecutionError(f'Cell {cell_id} failed.') from exc
  Imports:
    - from typing import Callable, Mapping
    - from layers.layer_0_core.level_0 import get_logger, ExecutionError [internal level_0]
  Line count: 27

### FILE: level_1/runtime/paths.py
  Module docstring: Environment-aware path resolution.
  Functions:
    - def get_environment_type() -> str: """ Get the current execution environment type. Returns: 'kaggle' or 'local' Example: >>> env = get_environment_type() >>> print(f"Running in {env} environment") """ return 'kaggle' if is_kaggle() else 'local'
    - def get_environment_paths() -> Dict[str, Path]: """ Get standard paths for the current environment. Returns: Dictionary mapping path purposes to actual paths: - 'working': Current working directory - 'data': Data input directory - 'output': Output directory - 'temp': Temporary directory Example: >>> paths = get_environment_paths() >>> data_dir = paths['data'] >>> output_dir = paths['output'] """ if is_kaggle(): return {'working': Path(os.getenv('KAGGLE_WORKING_DIR', '/kaggle/working')), 'data': Path(os.getenv('KAGGLE_INPUT_DIR', '/kaggle/input')), 'output': Path(os.getenv('KAGGLE_OUTPUT_DIR', '/kaggle/working')), 'temp': Path(os.getenv('KAGGLE_TEMP_DIR', '/kaggle/temp'))} else: return {'working': Path.cwd(), 'data': Path('data'), 'output': Path('output'), 'temp': Path('temp')}
    - def get_environment_root(purpose: str='output') -> Path: """ Get the root directory for a specific purpose. Args: purpose: One of 'working', 'data', 'output', 'temp' Returns: Path object for the requested root Raises: EnvironmentConfigError: If purpose is not recognized Example: >>> output_root = get_environment_root('output') >>> model_path = output_root / 'models' / 'best.pkl' """ paths = get_environment_paths() if purpose not in paths: raise EnvironmentConfigError(f"Unknown purpose '{purpose}'. Valid options: {list(paths.keys())}") return paths[purpose]
    - def resolve_environment_path(relative_path: Union[str, Path], purpose: str='output') -> Path: """ Resolve a relative path against environment root. Args: relative_path: Relative path from root purpose: Root directory purpose (default: 'output') Returns: Absolute path in current environment Example: >>> # In Kaggle: /kaggle/working/models/best.pkl >>> # Locally: output/models/best.pkl >>> path = resolve_environment_path('models/best.pkl') """ root = get_environment_root(purpose) return root / relative_path
    - def resolve_path(path: Union[str, Path], kaggle_path: Optional[Union[str, Path]]=None) -> Path: """ Resolve path based on environment with optional override. If kaggle_path is provided and running in Kaggle, use it. Otherwise use the default path. Args: path: Default path (for local) kaggle_path: Optional Kaggle-specific path Returns: Resolved Path object Example: >>> # Use different paths per environment >>> data_path = resolve_path('data/train.csv', '/kaggle/input/comp/train.csv') """ if is_kaggle() and kaggle_path is not None: return Path(kaggle_path) return Path(path)
    - def get_kaggle_working_submission_csv_path() -> Path: """ Return the canonical Kaggle working-dir submission path. """ return Path(os.getenv('KAGGLE_WORKING_DIR', '/kaggle/working')) / 'submission.csv'
    - def get_default_submission_csv_path(*, purpose: str='output') -> Path: """ Return the default environment-specific submission CSV path. - Kaggle: /kaggle/working/submission.csv (or KAGGLE_WORKING_DIR override) - Local: <output-root>/submission.csv """ if is_kaggle(): return get_kaggle_working_submission_csv_path() return resolve_environment_path('submission.csv', purpose=purpose)
  Imports:
    - import os
    - from pathlib import Path
    - from typing import Dict, Union, Optional
    - from level_0 import EnvironmentConfigError, is_kaggle [internal level_0]
  Line count: 151

### FILE: level_1/runtime/process.py
  Module docstring: Subprocess execution utilities.
  Functions:
    - def run_command(cmd: List[str], check: bool=True, timeout: Optional[int]=None) -> ProcessResult: """ Execute a command. Args: cmd: Command as list of strings check: Raise CalledProcessError on failure timeout: Optional timeout in seconds Returns: ProcessResult """ validate_command(cmd) result = subprocess.run(cmd, capture_output=True, text=True, check=check, timeout=timeout) return {'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
  Imports:
    - import subprocess
    - from typing import List, Optional
    - from layers.layer_0_core.level_0 import ProcessResult, validate_command [internal level_0]
  Line count: 43

### FILE: level_1/runtime/progress_config.py
  Module docstring: Progress display configuration.
  Classes:
    - ProgressVerbosity
    - ProgressConfig
        Methods:
                 def __post_init__(self) -> None: if self.refresh_rate <= 0: raise ConfigValidationError(f'refresh_rate must be positive, got {self.refresh_rate}')
                 @classmethod def from_env(cls, **overrides) -> 'ProgressConfig': """ Construct a ProgressConfig with environment variable overrides applied. PROGRESS_DISABLE=1|true|yes forces verbosity to SILENT. PROGRESS_VERBOSITY=<0-4 or name> sets verbosity if valid. Keyword arguments are applied after env resolution, allowing callers to combine env-driven defaults with explicit overrides. """ if _is_progress_disabled(): verbosity = ProgressVerbosity.SILENT else: verbosity = _parse_env_verbosity() or ProgressVerbosity.MODERATE return cls(verbosity=verbosity, **overrides)
  Functions:
    - def _parse_env_verbosity() -> Optional[ProgressVerbosity]: """ Read PROGRESS_VERBOSITY from the environment. Returns the parsed ProgressVerbosity, or None if unset or unrecognised. Logs a warning on unrecognised values — the caller applies its own default. """ val = os.environ.get('PROGRESS_VERBOSITY') if val is None: return None try: return ProgressVerbosity(int(val)) except ValueError: pass result = _VERBOSITY_MAP.get(val.strip().lower()) if result is None: logger.warning('Invalid PROGRESS_VERBOSITY=%r; use 0-4 or silent|minimal|moderate|detailed|debug. Ignoring.', val) return result
    - def _is_progress_disabled() -> bool: return os.environ.get('PROGRESS_DISABLE', '').strip().lower() in {'1', 'true', 'yes'}
  Imports:
    - import os
    - from dataclasses import dataclass
    - from enum import IntEnum
    - from typing import Optional
    - from layers.layer_0_core.level_0 import ConfigValidationError, get_logger [internal level_0]
  Line count: 115

### FILE: level_1/runtime/seed.py
  Module docstring: Reproducibility utilities.
  Functions:
    - def set_seed(seed: int, deterministic: bool=True) -> None: """ Set random seeds for reproducibility. Args: seed: Random seed value deterministic: Whether to enable deterministic torch backend behavior Raises: ValueError: If seed is not an int or not in [0, 2^32). """ if not isinstance(seed, int): raise ValueError(f'seed must be int, got {type(seed).__name__}') if not 0 <= seed < 2 ** 32: raise ValueError(f'seed must be in range [0, 2^32), got {seed}') os.environ['PYTHONHASHSEED'] = str(seed) random.seed(seed) np.random.seed(seed) torch = get_torch() if torch is None: return torch.manual_seed(seed) if torch.cuda.is_available(): torch.cuda.manual_seed(seed) torch.cuda.manual_seed_all(seed) if deterministic: torch.backends.cudnn.deterministic = True torch.backends.cudnn.benchmark = False
  Imports:
    - import os
    - import random
    - import numpy as np
    - from layers.layer_0_core.level_0 import get_torch [internal level_0]
  Line count: 43

### FILE: level_1/search/__init__.py
  Module docstring: Hyperparameter search profiles and variant generation utilities.
  Imports:
    - from . import profiles, variants
    - from .profiles import *
    - from .variants import *
  Line count: 12

### FILE: level_1/search/profiles/__init__.py
  Module docstring: Domain-specific hyperparameter grid profiles.
  Imports:
    - from .regression import get_regression_grid
    - from .search_type_utils import normalize_search_type
    - from .training import get_training_grid
    - from .transformer import get_transformer_hyperparameter_grid
    - from .vision import get_vision_grid
  Line count: 15
  __all__: ['get_regression_grid', 'normalize_search_type', 'get_training_grid', 'get_transformer_hyperparameter_grid', 'get_vision_grid']

### FILE: level_1/search/profiles/regression.py
  Module docstring: Regression model hyperparameter grid profiles.
  Module-level types / aliases:
    - _DEFAULTS: Dict[str, Dict[str, Any]]
    - _MODEL_TYPE_ALIASES: Dict[str, str]
    - _VARIED_BY_SEARCH_TYPE: Dict[str, Dict[str, Dict[str, List[Any]]]]
  Functions:
    - def get_regression_grid(model_type: str, search_type: str='quick') -> Dict[str, List[Any]]: """ Return a regression hyperparameter grid for the given model and search intensity. Args: model_type: One of 'lgbm', 'xgboost' (or alias 'xgb'), 'ridge'. search_type: One of 'defaults', 'quick', 'in_depth'. Returns: Dict mapping each hyperparameter name to a list of values to search. When search_type is 'defaults', each parameter maps to a single-item list containing only its default value. Raises: ValueError: If model_type or search_type is not recognised. """ resolved_type = _MODEL_TYPE_ALIASES.get(model_type, model_type) if resolved_type not in _DEFAULTS: valid_models = ', '.join((f"'{m}'" for m in _DEFAULTS)) raise ValueError(f"Unknown model_type: '{model_type}'. Must be one of {valid_models}.") defaults = _DEFAULTS[resolved_type] varied_by_model = resolve_varied_params(search_type, _VARIED_BY_SEARCH_TYPE) varied = varied_by_model.get(resolved_type, {}) return build_parameter_grid(defaults, varied)
  Imports:
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params [internal level_0]
  Line count: 115

### FILE: level_1/search/profiles/search_type_utils.py
  Module docstring: Search type normalization and validation.
  Functions:
    - def normalize_search_type(value: str) -> str: """ Normalize and validate a hyperparameter search type string. Raises ValueError if value is not a supported search type. """ normalized = (value or '').strip() if normalized not in VALID_HYPERPARAMETER_SEARCH_TYPES: raise ValueError(f"Unknown search_type: {value!r}. Must be one of: {', '.join(sorted(VALID_HYPERPARAMETER_SEARCH_TYPES))}") return normalized
  Imports:
    - from layers.layer_0_core.level_0 import VALID_HYPERPARAMETER_SEARCH_TYPES [internal level_0]
  Line count: 17

### FILE: level_1/search/profiles/training.py
  Module docstring: General training hyperparameter grid profile.
  Module-level types / aliases:
    - _DEFAULTS: Dict[str, Any]
    - _VARIED_BY_SEARCH_TYPE: Dict[str, Dict[str, List[Any]]]
  Functions:
    - def get_training_grid(search_type: str='defaults') -> Dict[str, List[Any]]: """ Return a training hyperparameter grid for the given search intensity. Args: search_type: One of 'defaults', 'quick', 'in_depth', 'thorough'. Returns: Dict mapping each hyperparameter name to a list of values to search. When search_type is 'defaults', each parameter maps to a single-item list containing only its default value. Raises: ValueError: If search_type is not recognised. """ return build_parameter_grid(_DEFAULTS, resolve_varied_params(search_type, _VARIED_BY_SEARCH_TYPE))
  Imports:
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params [internal level_0]
  Line count: 61

### FILE: level_1/search/profiles/transformer.py
  Module docstring: Transformer/ViT hyperparameter grid profile.
  Functions:
    - def _get_transformer_hyperparameter_defaults() -> Dict[str, Any]: """Default training hyperparameters for transformer/ViT models.""" return {'learning_rate': 0.001, 'batch_size': 32, 'optimizer': 'AdamW', 'weight_decay': 0.0001, 'loss_function': 'SmoothL1Loss', 'scheduler': 'ReduceLROnPlateau', 'scheduler_factor': 0.5, 'scheduler_patience': 5, 'early_stopping_patience': 10, 'num_epochs': 100}
    - def _get_varied_params_by_search_type() -> Dict[str, Dict[str, List[Any]]]: """Varied params per search type for transformer/ViT.""" return {'quick': {'learning_rate': [5e-05, 0.0001, 0.0002], 'batch_size': [8, 16], 'weight_decay': [0.01, 0.05]}, 'in_depth': {'learning_rate': [1e-05, 5e-05, 0.0001, 0.0005, 0.001, 0.005, 0.01], 'batch_size': [8, 16, 32, 64, 128], 'optimizer': ['AdamW', 'Adam', 'SGD'], 'weight_decay': [0, 1e-05, 0.0001, 0.001], 'scheduler_factor': [0.1, 0.5, 0.7], 'scheduler_patience': [3, 5, 7, 10]}, 'thorough': {'learning_rate': [1e-05, 5e-05, 0.0001, 0.0005, 0.001, 0.005], 'batch_size': [16, 32, 64], 'optimizer': ['AdamW', 'Adam', 'SGD'], 'weight_decay': [0, 1e-05, 0.0001, 0.001], 'loss_function': ['SmoothL1Loss', 'MSELoss'], 'scheduler': ['ReduceLROnPlateau', 'CosineAnnealingLR'], 'scheduler_factor': [0.1, 0.5, 0.7], 'scheduler_patience': [3, 5, 7, 10], 'early_stopping_patience': [5, 10, 15], 'num_epochs': [50, 100, 150]}}
    - def get_transformer_hyperparameter_grid(search_type: str='quick') -> Dict[str, List[Any]]: """ Transformer/ViT hyperparameter grid for grid search. Args: search_type: 'defaults', 'quick', 'in_depth', 'thorough', 'focused_in_depth', or 'focused_thorough' Returns: Dict mapping hyperparameter names to lists of values. All 10 parameters are always included. Raises: ValueError: For focused_* search types (use get_focused_parameter_grid) """ return build_parameter_grid(_get_transformer_hyperparameter_defaults(), resolve_varied_params(search_type, _get_varied_params_by_search_type()))
  Imports:
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params [internal level_0]
  Line count: 72

### FILE: level_1/search/profiles/vision.py
  Module docstring: Vision model hyperparameter grid profile.
  Module-level types / aliases:
    - _DEFAULTS: Dict[str, Any]
    - _VARIED_BY_SEARCH_TYPE: Dict[str, Dict[str, List[Any]]]
  Functions:
    - def get_vision_grid(search_type: str='quick') -> Dict[str, List[Any]]: """ Return a vision hyperparameter grid for the given search intensity. Args: search_type: One of 'defaults', 'quick', 'in_depth', 'thorough'. Returns: Dict mapping each hyperparameter name to a list of values to search. When search_type is 'defaults', each parameter maps to a single-item list containing only its default value. Raises: ValueError: If search_type is not recognised. """ return build_parameter_grid(_DEFAULTS, resolve_varied_params(search_type, _VARIED_BY_SEARCH_TYPE))
  Imports:
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params [internal level_0]
  Line count: 51

### FILE: level_1/search/variants/__init__.py
  Module docstring: Search variant generation, execution logging, and score tracking.
  Imports:
    - from .augmentation_variants import generate_variant_grid
    - from .execution_logging import log_variant_header
    - from .executor import execute_variants
    - from .param_grid import resolve_param_grid
    - from .scoring import select_best_score
  Line count: 15
  __all__: ['generate_variant_grid', 'log_variant_header', 'execute_variants', 'resolve_param_grid', 'select_best_score']

### FILE: level_1/search/variants/augmentation_variants.py
  Module docstring: Preprocessor and augmentation variant grid generation.
  Functions:
    - def generate_variant_grid(preprocessors: List[Any], augmenters: List[Any], excluded_preprocessors: Optional[Set[Any]]=None) -> List[Tuple[List[Any], List[Any]]]: """ Generate all (preprocessor combination, augmenter combination) variant pairs. Takes the power set of preprocessors and the power set of augmenters, then returns their cartesian product. Each element of the result is a tuple of (preprocessor_list, augmenter_list) representing one variant. Args: preprocessors: All available preprocessors to combine. augmenters: All available augmenters to combine. excluded_preprocessors: Preprocessors to exclude before generating combinations. Defaults to no exclusions. Returns: List of (preprocessor_subset, augmenter_subset) tuples covering every combination. Includes the empty-set case for both axes, so the total count is 2^|preprocessors| * 2^|augmenters| (after exclusions). """ excluded = excluded_preprocessors or set() active_preprocessors = [p for p in preprocessors if p not in excluded] pre_sets = generate_power_set(active_preprocessors) aug_sets = generate_power_set(augmenters) return [(list(pre), list(aug)) for pre in pre_sets for aug in aug_sets]
  Imports:
    - from typing import Any, List, Optional, Set, Tuple
    - from layers.layer_0_core.level_0 import generate_power_set [internal level_0]
  Line count: 42

### FILE: level_1/search/variants/execution_logging.py
  Module docstring: Grid search variant execution logging.
  Functions:
    - def log_variant_header(variant_index: int, total_variants: int, variant_info: str) -> None: """ Log a separator header marking the start of a grid search variant run. Args: variant_index: Zero-based index of the variant. total_variants: Total number of variants in this search. variant_info: Human-readable description of the variant being run. """ logger.info('=' * 60) logger.info('Variant %d/%d', variant_index + 1, total_variants) logger.info('%s', variant_info) logger.info('=' * 60)
  Imports:
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 24

### FILE: level_1/search/variants/executor.py
  Module docstring: Grid search executor.
  Functions:
    - def execute_variants(variants: List[Any], run_variant_fn: Callable[[Any, int], Dict[str, Any]], create_key_fn: Callable[[Any], Any], completed_variants: Set=None, save_results_fn: Callable[[], None]=lambda: None, save_checkpoint_fn: Callable[[], None]=lambda: None, score_key: str='score') -> Dict[str, Any]: """ Core grid search execution: returns best score, best variant, results, and updated completed set. """ completed_variants = completed_variants or set() results: List[Dict[str, Any]] = [] best_score = -float('inf') best_variant: Dict[str, Any] = {} skipped: Set[Any] = set() total_variants = len(variants) for idx, variant in enumerate(variants): variant_key = create_key_fn(variant) if variant_key in completed_variants: continue try: variant_result = run_variant_fn(variant, idx) variant_result['variant_key'] = str(variant_key) variant_result['variant_index'] = idx results.append(variant_result) score = variant_result.get(score_key, -float('inf')) if score > best_score: best_score = score best_variant = variant_result completed_variants.add(variant_key) save_results_fn() save_checkpoint_fn() except Exception as e: logger.warning('Variant %d failed: %s', idx, e, exc_info=True) results.append({'variant_key': str(variant_key), 'variant_index': idx, 'success': False, 'error': str(e), score_key: -float('inf')}) skipped.add(variant_key) save_results_fn() save_checkpoint_fn() return {'success': True, 'total_variants': total_variants, 'completed_variants': completed_variants, 'failed_variants': skipped, 'best_score': best_score, 'best_variant': best_variant, 'results': results}
  Imports:
    - from typing import Dict, List, Any, Callable, Set
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 76

### FILE: level_1/search/variants/param_grid.py
  Module docstring: Generic parameter grid resolution.
  Functions:
    - def resolve_param_grid(grid_config: Dict[str, Any], quick_mode: bool=False) -> Dict[str, List]: """ Resolve a parameter grid from config. Resolution order: 1. quick_param_grid (if quick_mode) 2. param_grid 3. error Framework-level: no domain assumptions. """ if quick_mode and 'quick_param_grid' in grid_config: logger.debug('Quick mode: resolved quick_param_grid') return grid_config['quick_param_grid'].copy() if 'param_grid' in grid_config: return grid_config['param_grid'].copy() raise ConfigValidationError("No parameter grid found. Expected: 'quick_param_grid' or 'param_grid'.")
  Imports:
    - from typing import Any, Dict, List
    - from layers.layer_0_core.level_0 import ConfigValidationError, get_logger [internal level_0]
  Line count: 37

### FILE: level_1/search/variants/scoring.py
  Module docstring: Grid search best score tracking.
  Functions:
    - def select_best_score(current_best_score: float, new_score: Optional[float], new_result: Dict[str, Any]) -> Tuple[float, Optional[Dict[str, Any]]]: """ Return the better score and its result dict. If new_score is greater than current_best_score, returns new_score and new_result. Otherwise returns current_best_score and None, signalling no improvement. Args: current_best_score: The best score recorded so far. new_score: The score from the latest variant. None if the variant failed. new_result: The result dict from the latest variant. Returns: Tuple of (best_score, best_result_or_None). """ if new_score is not None and new_score > current_best_score: logger.info('New best score: %.4f', new_score) return (new_score, new_result) return (current_best_score, None)
  Imports:
    - from typing import Any, Dict, Optional, Tuple
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 34

### FILE: level_1/training/__init__.py
  Module docstring: Training utilities. Full trainer classes live in level_2+.
  Imports:
    - from . import epochs
    - from .batch_processor import run_supervised_batch
    - from .checkpoint import load_model_checkpoint, save_checkpoint
    - from .epochs import *
    - from .forward_pass import forward_with_amp
    - from .model_io import load_vision_model, save_regression_model, save_vision_model
    - from .setup import setup_mixed_precision
  Line count: 24

### FILE: level_1/training/batch_processor.py
  Module docstring: Batch execution utilities.
  Functions:
    - def run_supervised_batch(model: Any, device: Any, criterion: Any, batch: Tuple) -> Tuple[Any, Any, Any]: """ Run forward pass and compute loss for a batch. Returns: outputs, targets, loss """ inputs, targets = extract_batch_data(batch, device) outputs = model(inputs) loss = None if targets is not None and criterion is not None: loss = criterion(outputs, targets) return (outputs, targets, loss)
  Imports:
    - from typing import Any, Tuple
    - from layers.layer_0_core.level_0 import extract_batch_data [internal level_0]
  Line count: 29

### FILE: level_1/training/checkpoint.py
  Module docstring: Checkpoint saving utilities with DataParallel handling.
  Functions:
    - def _strip_module_prefix(state_dict: Dict[str, Any]) -> Dict[str, Any]: """Remove the 'module.' prefix added by DataParallel from all state dict keys. When a model is saved while wrapped in DataParallel every key is prefixed with 'module.'. This helper produces a clean state dict that can be loaded into either a wrapped or unwrapped model. Args: state_dict: Model state dict, possibly with 'module.' prefixed keys. Returns: State dict with 'module.' prefix removed from all keys. If no keys have the prefix the original dict is returned unchanged. """ if not any((k.startswith('module.') for k in state_dict)): return state_dict return {k.removeprefix('module.'): v for k, v in state_dict.items()}
    - def save_checkpoint(model: nn.Module, optimizer: optim.Optimizer, scheduler: Optional[optim.lr_scheduler._LRScheduler], path: Path, epoch: int, best_score: float, history: List[Dict[str, Any]]) -> None: """Save a training checkpoint. Saves the underlying model state without the 'module.' prefix so the checkpoint is compatible with both DataParallel and non-parallel models. Args: model: PyTorch model (may be wrapped in DataParallel). optimizer: Optimizer whose state should be saved. scheduler: Optional scheduler whose state should be saved. path: Destination file path. epoch: Current epoch number. best_score: Best validation score achieved so far. history: List of per-epoch history dicts. """ raw_state = model.module.state_dict() if isinstance(model, nn.DataParallel) else model.state_dict() model_state_dict = _strip_module_prefix(raw_state) checkpoint: Dict[str, Any] = {'epoch': epoch, 'model_state_dict': model_state_dict, 'optimizer_state_dict': optimizer.state_dict(), 'best_score': best_score, 'history': history} if scheduler is not None: checkpoint['scheduler_state_dict'] = scheduler.state_dict() path = Path(path) ensure_dir(path.parent) torch.save(checkpoint, path) logger.debug('Saved checkpoint to %s', path)
    - def load_model_checkpoint(checkpoint_path: Path, model: torch.nn.Module, optimizer: Optional[torch.optim.Optimizer]=None, scheduler: Optional[torch.optim.lr_scheduler._LRScheduler]=None, device: Optional[torch.device]=None) -> Dict[str, Any]: """Load a training checkpoint into a model. Handles both DataParallel-wrapped and plain models. The 'module.' prefix is stripped before loading so that checkpoints saved from either model variant can be loaded into either variant. Args: checkpoint_path: Path to the checkpoint file. model: Model to load weights into (may be wrapped in DataParallel). optimizer: Optional optimizer to restore state into. scheduler: Optional scheduler to restore state into. device: Device to map the checkpoint tensors onto. Returns: Full checkpoint dict (epoch, best_score, history, etc.). Raises: FileNotFoundError: If checkpoint_path does not exist. """ checkpoint_path = Path(checkpoint_path) if not checkpoint_path.exists(): raise FileNotFoundError(f'Checkpoint not found: {checkpoint_path}') checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True) state_dict = _strip_module_prefix(checkpoint['model_state_dict']) target = model.module if isinstance(model, torch.nn.DataParallel) else model target.load_state_dict(state_dict) if optimizer is not None and 'optimizer_state_dict' in checkpoint: optimizer.load_state_dict(checkpoint['optimizer_state_dict']) if scheduler is not None and 'scheduler_state_dict' in checkpoint and (checkpoint['scheduler_state_dict'] is not None): scheduler.load_state_dict(checkpoint['scheduler_state_dict']) logger.info('Loaded checkpoint from %s', checkpoint_path) return checkpoint
  Imports:
    - from pathlib import Path
    - from typing import Any, Dict, List, Optional
    - from level_0 import ensure_dir, get_logger, get_torch [internal level_0]
  Line count: 137

### FILE: level_1/training/epochs/__init__.py
  Module docstring: Training epochs.
  Imports:
    - from .executor import train_one_epoch
    - from .logging import log_epoch_progress, log_epoch_progress_with_metric
  Line count: 10
  __all__: ['train_one_epoch', 'log_epoch_progress', 'log_epoch_progress_with_metric']

### FILE: level_1/training/epochs/executor.py
  Module docstring: Generic training loop executor.
  Functions:
    - def train_one_epoch(train_loader: DataLoader, batch_processor: Callable[[Any], 'torch.Tensor'], optimizer: torch.optim.Optimizer, scaler: Optional[Any]=None, use_tqdm: bool=False, tqdm_desc: Optional[str]=None) -> float: """ Execute one training epoch using a caller-defined batch processor. Use when training logic is custom: - multi-input models - custom losses - AMP - non-(X, y) datasets batch_processor(batch) -> scalar loss tensor """ if len(train_loader) == 0: raise ValueError('train_loader cannot be empty') total_loss = 0.0 num_batches = 0 iterator = train_loader if use_tqdm: from tqdm import tqdm iterator = tqdm(train_loader, desc=tqdm_desc or 'Train') for batch in iterator: loss = batch_processor(batch) if torch.isnan(loss): raise RuntimeError('NaN loss detected during training') optimizer.zero_grad() if scaler: scaler.scale(loss).backward() scaler.step(optimizer) scaler.update() else: loss.backward() optimizer.step() total_loss += loss.item() num_batches += 1 if num_batches == 0: raise ValueError('No batches processed') return total_loss / num_batches
  Imports:
    - from typing import Any, Callable, Optional
    - from layers.layer_0_core.level_0 import get_torch [internal level_0]
  Line count: 69

### FILE: level_1/training/epochs/logging.py
  Module docstring: Generic epoch progress logging.
  Functions:
    - def log_epoch_progress(*, epoch: int, num_epochs: int, train_loss: float, val_loss: float, metric_name: Optional[str], metric_value: Optional[float], optimizer, log_interval: int=10) -> None: """ Log training progress for an epoch. Args: metric_name: Name of primary metric (e.g. 'R2', 'Accuracy') metric_value: Value of primary metric """ if optimizer is None: return if epoch % log_interval != 0 and epoch != num_epochs - 1: return current_lr = optimizer.param_groups[0]['lr'] parts = [f'Epoch [{epoch}/{num_epochs}]', f'Train Loss: {train_loss:.4f}', f'Val Loss: {val_loss:.4f}'] if metric_name and metric_value is not None: parts.append(f'{metric_name}: {metric_value:.4f}') parts.append(f'LR: {current_lr:.6f}') logger.info(', '.join(parts))
    - def log_epoch_progress_with_metric(*, epoch: int, num_epochs: int, train_loss: float, val_loss: float, metric_name: str, metric_value: float, optimizer, log_interval: int=10) -> None: """ Log epoch progress with a custom metric. Convenience wrapper for log_epoch_progress when metric_name/metric_value are known (e.g. "Weighted R²", weighted_r2). """ log_epoch_progress(epoch=epoch, num_epochs=num_epochs, train_loss=train_loss, val_loss=val_loss, metric_name=metric_name, metric_value=metric_value, optimizer=optimizer, log_interval=log_interval)
  Imports:
    - from typing import Optional
    - from layers.layer_0_core.level_0 import get_logger [internal level_0]
  Line count: 80

### FILE: level_1/training/forward_pass.py
  Module docstring: Forward pass with optional AMP.
  Functions:
    - def forward_with_amp(model: nn.Module, inputs: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], use_amp: bool=False) -> torch.Tensor: """ Forward pass through model with optional automatic mixed precision. Args: model: PyTorch model. inputs: Model inputs (single tensor or tuple of tensors for dual-input models). use_amp: Whether to use automatic mixed precision (FP16). Returns: Model outputs. """ if use_amp: with torch.amp.autocast('cuda'): return model(inputs) return model(inputs)
  Imports:
    - from typing import Union, Tuple
    - from layers.layer_0_core.level_0 import get_torch [internal level_0]
  Line count: 30

### FILE: level_1/training/model_io.py
  Module docstring: Model input/output utilities.
  Functions:
    - def save_regression_model(model: Any, save_dir: Path) -> None: """ Save trained regression model and metadata. Args: model: Trained regression model. save_dir: Directory to save model to. """ ensure_dir(save_dir) model_path = save_dir / 'regression_model.pkl' with open(model_path, 'wb') as f: pickle.dump(model, f) metadata = {'model_type': type(model).__name__, 'model_path': str(model_path)} metadata_path = save_dir / 'metadata.json' with open(metadata_path, 'w') as f: json.dump(metadata, f, indent=2)
    - def save_vision_model(model: Any, path: str) -> None: """ Save a vision model's state dict to path. Args: model: PyTorch model whose state dict should be saved. path: Destination file path (e.g. 'checkpoints/best_model.pth'). """ torch = get_torch() ensure_dir(Path(path).parent) torch.save(model.state_dict(), path)
    - def load_vision_model(model: Any, path: str, device: str='cpu') -> None: """ Load a vision model's state dict from path into model in-place. Args: model: PyTorch model to load weights into. path: Source file path. device: Device to map tensors onto (default: 'cpu'). Raises: FileNotFoundError: If path does not exist. """ torch = get_torch() path = Path(path) if not path.exists(): raise FileNotFoundError(f'Model state dict not found: {path}') state_dict = torch.load(path, map_location=device, weights_only=True) model.load_state_dict(state_dict)
  Imports:
    - import json
    - import pickle
    - from pathlib import Path
    - from typing import Any
    - from layers.layer_0_core.level_0 import ensure_dir, get_torch [internal level_0]
  Line count: 84

### FILE: level_1/training/setup.py
  Module docstring: Training component setup utilities.
  Functions:
    - def setup_mixed_precision(config: Any, device: Any) -> Tuple[bool, Optional[Any]]: """ Set up mixed precision training (GradScaler). Returns: use_mixed_precision: bool scaler: torch.amp.GradScaler or None """ torch = get_torch() use_mixed_precision = get_config_value(config, 'training.use_mixed_precision', default=False) scaler = None if use_mixed_precision and device.type == 'cuda': try: scaler = torch.amp.GradScaler() logger.info('Mixed precision (FP16) training enabled') except Exception: logger.warning('Mixed precision requested but not available') use_mixed_precision = False return (use_mixed_precision, scaler)
  Imports:
    - from typing import Any, Optional, Tuple
    - from layers.layer_0_core.level_0 import get_logger, get_torch, get_config_value [internal level_0]
  Line count: 43

## 3. __init__.py Public API Summary

### INIT: level_1/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .cli import *
    - from .data import *
    - from .evaluation import *
    - from .features import *
    - from .grid_search import *
    - from .guards import *
    - from .io import *
    - from .ontology import *
    - from .pipelines import *
    - from .protein import *
    - from .runtime import *
    - from .search import *
    - from .training import *
### INIT: level_1/cli/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .builders import *
    - from .subparsers import setup_framework_subparsers
### INIT: level_1/cli/builders/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .ensemble import *
    - from .grid_search import GridSearchCommandBuilder
    - from .regression_ensemble import RegressionEnsembleCommandBuilder
    - from .stacking import StackingCommandBuilder
    - from .submission import SubmissionCommandBuilder
    - from .train_export import TrainExportCommandBuilder
### INIT: level_1/cli/builders/ensemble/__init__.py
  Exports (explicit __all__): EnsembleCommandBuilder, ensure_positive_weights, normalize_weights
  Relative imports:
    - from .builder import EnsembleCommandBuilder
    - from .weights import ensure_positive_weights, normalize_weights
### INIT: level_1/data/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .cv_splits import *
    - from .domain import *
    - from .io import *
    - from .processing import *
### INIT: level_1/data/cv_splits/__init__.py
  Exports (explicit __all__): split_features_by_fold, create_kfold_splits, get_fold_data
  Relative imports:
    - from .arrays import split_features_by_fold
    - from .dataframes import create_kfold_splits, get_fold_data
### INIT: level_1/data/domain/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .tabular import *
    - from .vision import *
### INIT: level_1/data/domain/tabular/__init__.py
  Exports (explicit __all__): TabularModelConfig, TabularDataConfig, TabularConfig, TabularDataset
  Relative imports:
    - from .config import TabularModelConfig, TabularDataConfig, TabularConfig
    - from .tabular_dataset import TabularDataset
### INIT: level_1/data/domain/vision/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .config import VisionConfig, VisionDataConfig, VisionModelConfig
    - from .models import *
### INIT: level_1/data/domain/vision/models/__init__.py
  Exports (explicit __all__): BaseHead, ClassificationHead, RegressionHead, BaseVisionModel, configure_huggingface_cache, resolve_offline_weight_cache
  Relative imports:
    - from .base_head import BaseHead, ClassificationHead, RegressionHead
    - from .base import BaseVisionModel
    - from .weight_cache import configure_huggingface_cache, resolve_offline_weight_cache
### INIT: level_1/data/io/__init__.py
  Exports (explicit __all__): BatchLoader, load_batch, build_embedding_error_message, load_ids_file, load_embeddings_file
  Relative imports:
    - from .batch_loading import BatchLoader, load_batch
    - from .numpy_loader import build_embedding_error_message, load_ids_file, load_embeddings_file
### INIT: level_1/data/processing/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .augmentation import *
    - from .datasets import *
    - from .preprocessing import *
### INIT: level_1/data/processing/augmentation/__init__.py
  Exports (explicit __all__): get_blur_transform, get_color_jitter_transform, get_geometric_transform, AddGaussianNoise, get_noise_transform, compose_transform_pipeline
  Relative imports:
    - from .blur import get_blur_transform
    - from .color import get_color_jitter_transform
    - from .geometric import get_geometric_transform
    - from .noise import AddGaussianNoise, get_noise_transform
    - from .pipeline import compose_transform_pipeline
### INIT: level_1/data/processing/datasets/__init__.py
  Exports (explicit __all__): BaseImageDataset, ImagePathDataset, BaseStreamingDataset, StreamingDataset, StreamingSplitDataset
  Relative imports:
    - from .image_datasets import BaseImageDataset, ImagePathDataset
    - from .streaming_datasets import BaseStreamingDataset, StreamingDataset, StreamingSplitDataset
### INIT: level_1/data/processing/preprocessing/__init__.py
  Exports (explicit __all__): contrast_enhancement, crop_relative_height, inpaint_by_hsv_range, normalize, get_normalize_transform, resize, get_resize_transform
  Relative imports:
    - from .contrast_enhancement import contrast_enhancement
    - from .image_base import crop_relative_height, inpaint_by_hsv_range
    - from .normalization import (
    - from .resizing import resize, get_resize_transform
### INIT: level_1/evaluation/__init__.py
  Exports (explicit __all__): LossType, BaseLoss, FocalLoss, WeightedBCELoss, SparseBCEWithLogitsLoss, LabelSmoothingBCEWithLogitsLoss, MetricRegistry, register_metric, get_metric, list_metrics, calculate_fold_statistics, generate_cv_test_gap_warnings
  Relative imports:
    - from .loss_types import (
    - from .metric_registry import (
    - from .results_analysis import (
### INIT: level_1/features/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .cache import *
    - from .base_feature_extractor import BaseFeatureExtractor
    - from .feature_registry import INDIVIDUAL_FEATURES, FEATURE_PRESETS, get_feature_preset, parse_feature_spec
    - from .film import FiLM
    - from .fuse_embeddings import fuse_embeddings
    - from .physicochemical_features import calculate_physicochemical_properties, calculate_ctd_features
    - from .siglip_classes import get_siglip_image_classes, get_siglip_text_classes
### INIT: level_1/features/cache/__init__.py
  Exports (explicit __all__): set_feature_cache_path_provider, set_model_id_map, get_model_id, get_cache_base_paths, get_model_name_from_model_id, get_metadata_dir, generate_feature_filename, parse_feature_filename
  Relative imports:
    - from .config import (
    - from .filename import generate_feature_filename, parse_feature_filename
### INIT: level_1/grid_search/__init__.py
  Exports (explicit __all__): get_pareto_frontier
  Relative imports:
    - from .pareto_frontier import get_pareto_frontier
### INIT: level_1/guards/__init__.py
  Exports (explicit __all__): check_array_finite, check_min_collection_length, validate_config_section_exists, validate_feature_extraction_trainer_inputs, validate_predictions_for_ensemble, validate_paired_predictions, check_not_none, validate_execution_result
  Relative imports:
    - from .arrays import check_array_finite
    - from .collections import check_min_collection_length
    - from .config import (
    - from .ensembles import validate_predictions_for_ensemble, validate_paired_predictions
    - from .none import check_not_none
    - from .result_checks import validate_execution_result
### INIT: level_1/io/__init__.py
  Exports (explicit __all__): TsvSubmissionFormatter
  Relative imports:
    - from .tsv_submission_formatter import TsvSubmissionFormatter
### INIT: level_1/ontology/__init__.py
  Exports (explicit __all__): HierarchyPropagator, OntologyConfigResolver
  Relative imports:
    - from .config_resolver import OntologyConfigResolver
    - from .hierarchy_propagator import HierarchyPropagator
### INIT: level_1/pipelines/__init__.py
  Exports (explicit __all__): merge_pipeline_results_ok, run_pipeline_result_with_validation_first, run_two_stage_pipeline_result_with_validation_first, BasePipeline, ValidateFirstRunner, ValidateFirstPipelineResultShell, TwoStageValidateFirstPipelineResultShell
  Relative imports:
    - from .orchestration import (
    - from .pipeline_shells import (
### INIT: level_1/protein/__init__.py
  Exports (explicit __all__): normalize_protein_id, normalize_protein_ids, find_common_protein_ids, align_embeddings_to_common_ids
  Relative imports:
    - from .id_utils import (
### INIT: level_1/runtime/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .config import *
    - from .cuda import *
    - from .base_pipeline import BasePipeline
    - from .chunked_prediction import predict_in_chunks, predict_proteins_in_chunks
    - from .device import is_cuda_available, get_device_info, get_device
    - from .lazy_imports import lazy_import
    - from .metadata_paths import find_metadata_candidates
    - from .notebook_runner import safe_execute_cell
    - from .paths import (
    - from .process import run_command
    - from .progress_config import ProgressVerbosity, ProgressConfig
    - from .seed import set_seed
### INIT: level_1/runtime/config/__init__.py
  Exports (explicit __all__): create_config, format_config_section, log_config_section, print_config_section, EvaluationConfig, GridSearchConfig, TrainingConfig
  Relative imports:
    - from .config_creation import create_config
    - from .config_sections import (
    - from .evaluation import EvaluationConfig
    - from .grid_search import GridSearchConfig
    - from .training import TrainingConfig
### INIT: level_1/runtime/cuda/__init__.py
  Exports (explicit __all__): cleanup_gpu_memory, perform_aggressive_cleanup, get_model_memory_usage, estimate_memory_mb, get_available_memory_mb, get_total_memory_mb, get_memory_usage_percent, print_gpu_memory_status
  Relative imports:
    - from .gpu_cleanup import (
    - from .memory import (
    - from .monitoring import (
### INIT: level_1/search/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .profiles import *
    - from .variants import *
### INIT: level_1/search/profiles/__init__.py
  Exports (explicit __all__): get_regression_grid, normalize_search_type, get_training_grid, get_transformer_hyperparameter_grid, get_vision_grid
  Relative imports:
    - from .regression import get_regression_grid
    - from .search_type_utils import normalize_search_type
    - from .training import get_training_grid
    - from .transformer import get_transformer_hyperparameter_grid
    - from .vision import get_vision_grid
### INIT: level_1/search/variants/__init__.py
  Exports (explicit __all__): generate_variant_grid, log_variant_header, execute_variants, resolve_param_grid, select_best_score
  Relative imports:
    - from .augmentation_variants import generate_variant_grid
    - from .execution_logging import log_variant_header
    - from .executor import execute_variants
    - from .param_grid import resolve_param_grid
    - from .scoring import select_best_score
### INIT: level_1/training/__init__.py
  Exports: star-import / side-effect re-exports only (no explicit __all__ in this file)
  Relative imports:
    - from .batch_processor import run_supervised_batch
    - from .checkpoint import load_model_checkpoint, save_checkpoint
    - from .epochs import *
    - from .forward_pass import forward_with_amp
    - from .model_io import load_vision_model, save_regression_model, save_vision_model
    - from .setup import setup_mixed_precision
### INIT: level_1/training/epochs/__init__.py
  Exports (explicit __all__): train_one_epoch, log_epoch_progress, log_epoch_progress_with_metric
  Relative imports:
    - from .executor import train_one_epoch
    - from .logging import log_epoch_progress, log_epoch_progress_with_metric

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From level_0 (including `from level_0 import ...` and `from layers.layer_0_core.level_0 import ...`):
    Symbols and types pulled across the package include (non-exhaustive, by module group):
    Logging/runtime: get_logger, get_torch, is_kaggle, is_torch_available, load_image_pil, get_nn_module_base_class,
      get_vision_module_and_tensor_types, IMAGENET_MEAN, IMAGENET_STD
    Errors/validation: DataValidationError, ConfigValidationError, ExecutionError, DeviceError, EnvironmentConfigError
    Config: CompositeConfig, EvaluationSchema, TrainingSchema, PathConfig, RuntimeConfig, TrainingSchema, get_arg,
      get_config_value, Metric, PipelineResult, ProcessResult, validate_command
    Training/grid: extract_batch_data, build_parameter_grid, resolve_varied_params, VALID_HYPERPARAMETER_SEARCH_TYPES,
      generate_power_set, filter_successful_results, worst_case_metric_sentinel
    CLI: BaseCommandBuilder, add_common_arguments, add_model_type_argument, add_model_path_argument,
      add_ensemble_method_argument
    I/O & execution: ensure_dir, ExecutionResult, align_embeddings, find_common_ids
    Biology/embeddings: AA_GROUPS, AA_WEIGHTS, HYDROPATHY_VALUES, parse_obo_file
  From same level (level_1) in logic files:
    - No `from level_1 import ...` or `import level_1` patterns observed.
    - Relative imports (`from .`) appear in __init__.py and package aggregation only — consistent with IMPORT_STYLE rules for inits.
  From level_2 or higher:
    - No imports from level_2+ detected in .py sources (docstring in training/__init__.py mentions level_2+ only descriptively).
```

## 5. Flags

```
FLAGS:
  evaluation/loss_types.py — 303 lines (>300)
  grid_search/__init__.py — 5 lines (<10; minimal barrel)
  Duplicate class name: BasePipeline — runtime/base_pipeline.py (abstract execute/setup pipeline) vs
    pipelines/pipeline_shells.py (generic shell with run(); different abstractions, same name)
  ontology/config_resolver.py — imports only typing (no level_0); self-contained resolver
  data/io/batch_loading.py — BatchLoader is a typing.Protocol, not a concrete class
  Word matches (compat / compatible) in prose only: training/checkpoint.py, guards/ensembles.py (not deprecation markers)
  No `deprecated`, `legacy`, `shim`, `TODO: remove`, or `backwards` keyword hits in level_1 .py sources beyond generic wording above
  Catch-all package names: none named utils/helpers/misc/common at top level; `io` package is generic but intentional
```

## 6. Static scan summary (precheck)

- **precheck_status:** skipped_machine_script (environment: `ModuleNotFoundError: No module named 'torchvision'`).
- Machine violation list / scan results: **unavailable** for this run; no automated violation kinds to merge.
