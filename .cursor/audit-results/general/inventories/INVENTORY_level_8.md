---
generated: 2026-04-08
audit_scope: general
level_name: level_8
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_8_2026-04-08.md
---

# INVENTORY: level_8

## 1. Package & File Tree

```
level_8/
  README.md
  __init__.py
  grid_search/
    README.md
    __init__.py
    dataset_grid_search.py
    end_to_end_variant_helpers.py
  regression/
    README.md
    __init__.py
    regression_ensemble.py
    regression_variant_helpers.py
  training/
    README.md
    __init__.py
    cv_splits.py
    detect_train_export_mode.py
    train_pipeline.py
```

## 2. Per-File Details

```
FILE: level_8/__init__.py
  Module docstring: Level 8: Training pipeline, grid search, regression ensemble.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .grid_search import DatasetGridSearch, create_end_to_end_variant_result, extract_variant_config [internal]
    - from .regression import (RegressionEnsemble, create_regression_ensemble_from_paths, create_regression_variant_result, run_regression_cv_fold) [internal]
    - from .training import (TrainPipeline, create_robust_cv_splits, detect_train_export_mode) [internal]
  Line count: 25
  __all__: ["TrainPipeline", "create_robust_cv_splits", "detect_train_export_mode", "run_regression_cv_fold", "create_regression_variant_result", "extract_variant_config", "create_end_to_end_variant_result", "RegressionEnsemble", "create_regression_ensemble_from_paths", "DatasetGridSearch"]
```

```
FILE: level_8/grid_search/__init__.py
  Module docstring: Grid search implementations and variant helpers.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .dataset_grid_search import DatasetGridSearch [internal]
    - from .end_to_end_variant_helpers import create_end_to_end_variant_result, extract_variant_config [internal]
  Line count: 8
  __all__: ["DatasetGridSearch", "extract_variant_config", "create_end_to_end_variant_result"]
```

```
FILE: level_8/grid_search/dataset_grid_search.py
  Module docstring: DatasetGridSearch extends framework GridSearchBase; config must have paths set by caller (contest_context).
  Classes:
    - DatasetGridSearch
        Methods:
          __init__(self, train_pipeline_fn: Optional[Any] = None, **kwargs)
          _get_grid_search_type(self) -> str
          _get_results_filename(self) -> str
          _generate_variant_grid(self) -> List[Tuple[List[str], List[str]]]
          _create_variant_key(self, variant: Tuple[List[str], List[str]]) -> Tuple
          _create_variant_key_from_result(self, result: Dict[str, Any]) -> Optional[Tuple]
          _run_variant(self, variant: Tuple[List[str], List[str]], variant_index: int, total_variants: Optional[int] = None, actual_variant_num: Optional[int] = None, total_to_test: Optional[int] = None) -> Dict[str, Any]
  Functions: (none)
  Imports:
    - from typing import Dict, List, Any, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, GRID_SEARCH_TYPE_DATASET, RESULTS_FILE_GRIDSEARCH [internal]
    - from layers.layer_0_core.level_1 import generate_variant_grid [internal]
    - from layers.layer_0_core.level_6 import GridSearchBase, create_variant_key, create_variant_key_from_result, get_default_hyperparameters [internal]
    - from layers.layer_0_core.level_7 import run_single_variant [internal]
  Line count: 90
  __all__: (not defined)
```

```
FILE: level_8/grid_search/end_to_end_variant_helpers.py
  Module docstring: Helper functions for end-to-end variant execution.
  Classes: (none)
  Functions:
    - _apply_hyperparameters_to_config(config: Any, hyperparameters: Dict[str, Any]) -> None
    - extract_variant_config(variant_config: Any, param_names: list, variant: tuple, variant_index: int) -> Tuple[Any, str, int, int, str, str]
    - create_end_to_end_variant_result(variant_index: int, variant_id: str, cv_score: Optional[float], fold_scores: Optional[list], hyperparameters: Dict[str, Any], config: Any, batch_size_used: int, error: Optional[str] = None) -> Dict[str, Any]
  Imports:
    - import copy [stdlib]
    - from typing import Dict, Any, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import ConfigValidationError, get_logger [internal]
    - from layers.layer_0_core.level_7 import build_success_result, build_error_result [internal]
  Line count: 112
  __all__: (not defined)
```

```
FILE: level_8/regression/__init__.py
  Module docstring: Regression variant execution and ensemble.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .regression_ensemble import RegressionEnsemble, create_regression_ensemble_from_paths [internal]
    - from .regression_variant_helpers import create_regression_variant_result, run_regression_cv_fold [internal]
  Line count: 9
  __all__: ["run_regression_cv_fold", "create_regression_variant_result", "RegressionEnsemble", "create_regression_ensemble_from_paths"]
```

```
FILE: level_8/regression/regression_ensemble.py
  Module docstring: Regression ensemble: load regression models, predict, and combine predictions.
  Classes:
    - RegressionEnsemble
        Methods:
          __init__(self, model_paths: List[str], model_configs: List[Dict[str, Any]], ensembling_method: EnsemblingMethod, feature_extraction_model_name: str, cv_scores: Optional[List[float]] = None, pickle_module_aliases: Optional[Dict[str, Any]] = None)
          _load_models(self) -> None
          _resolve_model_file(model_path: str) -> Path  [staticmethod]
          predict(self, features: np.ndarray, return_individual: bool = False) -> np.ndarray
  Functions:
    - create_regression_ensemble_from_paths(model_paths: List[str], model_configs: List[Dict[str, Any]], method: str = "weighted_average", feature_extraction_model_name: Optional[str] = None, cv_scores: Optional[List[float]] = None, pickle_module_aliases: Optional[Dict[str, Any]] = None) -> RegressionEnsemble
  Imports:
    - import sys [stdlib]
    - import numpy as np [third-party]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, EnsemblingMethod [internal]
    - from layers.layer_0_core.level_4 import load_pickle [internal]
    - from layers.layer_0_core.level_6 import SimpleAverageEnsemble [internal]
    - from layers.layer_0_core.level_7 import create_ensembling_method [internal]
  Line count: 131
  __all__: (not defined)
```

```
FILE: level_8/regression/regression_variant_helpers.py
  Module docstring: Helper functions for regression head variant execution.
  Classes: (none)
  Functions:
    - run_regression_cv_fold(fold: int, n_folds: int, all_features: np.ndarray, all_targets: np.ndarray, fold_assignments: np.ndarray, regression_model_type: str, hyperparameters: Dict[str, Any], config: Any, metric_calculator: Any) -> float
    - create_regression_variant_result(variant_index: int, variant_id: str, cv_score: float, fold_scores: list, hyperparameters: Dict[str, Any], config: Any, feature_filename: str, regression_model_type: str) -> Dict[str, Any]
  Imports:
    - import numpy as np [third-party]
    - from typing import Dict, Any [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import split_features_by_fold [internal]
    - from layers.layer_0_core.level_3 import create_regression_model [internal]
    - from layers.layer_0_core.level_7 import build_success_result [internal]
  Line count: 91
  __all__: (not defined)
```

```
FILE: level_8/training/__init__.py
  Module docstring: Training pipelines and workflows.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .cv_splits import create_robust_cv_splits [internal]
    - from .detect_train_export_mode import detect_train_export_mode [internal]
    - from .train_pipeline import TrainPipeline [internal]
  Line count: 9
  __all__: ["TrainPipeline", "create_robust_cv_splits", "detect_train_export_mode"]
```

```
FILE: level_8/training/cv_splits.py
  Module docstring: CV split creation: visual clustering and hierarchical stratification.
  Classes: (none)
  Functions:
    - create_robust_cv_splits(data: 'pd.DataFrame', target_names: List[str], target_weights: Dict[str, float], embedding_cols: Optional[List[str]] = None, n_splits: int = 5, n_clusters: int = 30, seed: int = 42, use_hierarchical: bool = False) -> 'pd.DataFrame'
    - _create_hierarchical_cv_splits(df: 'pd.DataFrame', target_names: List[str], n_splits: int, seed: int) -> 'pd.DataFrame'
  Imports:
    - import pandas as pd [third-party]
    - import numpy as np [third-party]
    - from typing import Dict, List, Optional [stdlib]
    - from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold [third-party]
    - from sklearn.cluster import KMeans [third-party]
    - from sklearn.decomposition import PCA [third-party]
    - from layers.layer_0_core.level_0 import get_logger [internal]
  Line count: 123
  __all__: (not defined)
```

```
FILE: level_8/training/detect_train_export_mode.py
  Module docstring: Train/export mode detection utilities.
  Classes: (none)
  Functions:
    - detect_train_export_mode(model_name: Optional[str], fresh_train: bool) -> str
  Imports:
    - from typing import Optional [stdlib]
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import print_config_section [internal]
    - from layers.layer_0_core.level_7 import auto_detect_grid_search_results [internal]
  Line count: 57
  __all__: (not defined)
```

```
FILE: level_8/training/train_pipeline.py
  Module docstring: Atomic training pipeline for vision and tabular models.
  Classes:
    - TrainPipeline
        Methods:
          __init__(self, config: Any, model_type: str = 'vision', **kwargs)
          setup(self) -> None
          execute(self) -> Dict[str, Any]
          _train_vision(self) -> Dict[str, Any]
          _train_tabular(self) -> Dict[str, Any]
          cleanup(self) -> None
  Functions: (none)
  Imports:
    - from typing import Dict, Any [stdlib]
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger [internal]
    - from layers.layer_0_core.level_1 import validate_config_section_exists, get_device, BasePipeline [internal]
    - from layers.layer_0_core.level_2 import create_optimizer, create_scheduler, create_loss_function [internal]
    - from layers.layer_0_core.level_4 import create_vision_model, save_pickle, create_dataloaders [internal]
    - from layers.layer_0_core.level_5 import VisionTrainer [internal]
    - from layers.layer_0_core.level_7 import create_tabular_model [internal]
  Line count: 133
  __all__: (not defined)
```

## 3. __init__.py Public API Summary

```
INIT: level_8/__init__.py
  Exports: TrainPipeline, create_robust_cv_splits, detect_train_export_mode, run_regression_cv_fold, create_regression_variant_result, extract_variant_config, create_end_to_end_variant_result, RegressionEnsemble, create_regression_ensemble_from_paths, DatasetGridSearch
  Re-exports from: level_8.grid_search, level_8.regression, level_8.training
```

```
INIT: level_8/grid_search/__init__.py
  Exports: DatasetGridSearch, extract_variant_config, create_end_to_end_variant_result
  Re-exports from: level_8.grid_search.dataset_grid_search, level_8.grid_search.end_to_end_variant_helpers
```

```
INIT: level_8/regression/__init__.py
  Exports: run_regression_cv_fold, create_regression_variant_result, RegressionEnsemble, create_regression_ensemble_from_paths
  Re-exports from: level_8.regression.regression_ensemble, level_8.regression.regression_variant_helpers
```

```
INIT: level_8/training/__init__.py
  Exports: TrainPipeline, create_robust_cv_splits, detect_train_export_mode
  Re-exports from: level_8.training.cv_splits, level_8.training.detect_train_export_mode, level_8.training.train_pipeline
```

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0: get_logger, GRID_SEARCH_TYPE_DATASET, RESULTS_FILE_GRIDSEARCH, ConfigValidationError, ensure_dir, EnsemblingMethod
  From layers.layer_0_core.level_1: generate_variant_grid, print_config_section, validate_config_section_exists, get_device, BasePipeline, split_features_by_fold
  From layers.layer_0_core.level_2: create_optimizer, create_scheduler, create_loss_function
  From layers.layer_0_core.level_3: create_regression_model
  From layers.layer_0_core.level_4: load_pickle, create_vision_model, save_pickle, create_dataloaders
  From layers.layer_0_core.level_5: VisionTrainer
  From layers.layer_0_core.level_6: GridSearchBase, create_variant_key, create_variant_key_from_result, get_default_hyperparameters, SimpleAverageEnsemble
  From layers.layer_0_core.level_7: run_single_variant, build_success_result, build_error_result, create_ensembling_method, auto_detect_grid_search_results
  From same level (level_8): relative imports in __init__.py files and cross-subpackage relative imports within grid_search/regression/training
  From level_9 or higher: (none observed)
```

## 5. FLAGS

```
FLAGS:
  level_8/grid_search/__init__.py — 8 lines (minimal)
  level_8/grid_search/end_to_end_variant_helpers.py — filename contains "helpers"
  level_8/regression/regression_variant_helpers.py — filename contains "helpers"
  level_8/training/train_pipeline.py — 133 lines; references emoji in log strings (observational only)
  Keywords (deprecated, legacy, compat, backwards, TODO: remove, shim): (none found)
  Public name overlap: create_end_to_end_variant_result (function) defined in end_to_end_variant_helpers; exported at level_8 root
```

## 6. Static scan summary (precheck)

- Source: `precheck_level_8_2026-04-08.md` under general summaries.
- `precheck_status`: skipped_machine_script (`ModuleNotFoundError: No module named 'torchvision'`).
- Machine Phase 7 reconciliation / devtools precheck stack did not run in the environment that produced the precheck artifact.
