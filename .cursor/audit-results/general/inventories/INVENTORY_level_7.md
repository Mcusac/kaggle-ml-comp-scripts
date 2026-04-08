---
generated: 2026-04-08
audit_scope: general
level_name: level_7
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_7_2026-04-08.md
---

# INVENTORY: level_7

## 1. Package & File Tree

```
level_7/
  README.md
  __init__.py
  factories/
    README.md
    __init__.py
    create_ensembling_method.py
    tabular_model_factory.py
  grid_search/
    README.md
    __init__.py
    dataset_variant_executor.py
    hyperparameter_base.py
    variant_result_builders.py
```

## 2. Per-File Details

```
FILE: level_7/__init__.py
  Module docstring: Level 7: Grid search results detection, variant builders, hyperparameter base, tabular model factory.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .factories import create_ensembling_method, create_tabular_model [internal]
    - from .grid_search import (HyperparameterGridSearchBase, auto_detect_grid_search_results, build_error_result, build_success_result, calculate_focused_grid_size, get_completed_count, run_final_cleanup, run_single_variant, run_variant_cleanup) [internal]
  Line count: 26
  __all__: ["calculate_focused_grid_size", "auto_detect_grid_search_results", "build_success_result", "build_error_result", "create_ensembling_method", "HyperparameterGridSearchBase", "run_single_variant", "create_tabular_model", "run_variant_cleanup", "run_final_cleanup", "get_completed_count"]
```

```
FILE: level_7/factories/__init__.py
  Module docstring: Factories for tabular models and ensembling methods.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .create_ensembling_method import create_ensembling_method [internal]
    - from .tabular_model_factory import create_tabular_model [internal]
  Line count: 4
  __all__: ["create_tabular_model", "create_ensembling_method"]
```

```
FILE: level_7/factories/tabular_model_factory.py
  Module docstring: Tabular model factory. Uses level_5, level_6.
  Classes: (none)
  Functions:
    - create_tabular_model(model_type: str, input_dim: int, output_dim: int, **kwargs) -> BaseTabularModel
  Imports:
    - from layers.layer_0_core.level_5 import BaseTabularModel [internal]
    - from layers.layer_0_core.level_6 import (MLPModel, LogisticRegressionModel, RidgeModel, XGBoostModel, LightGBMModel) [internal]
  Line count: 47
  __all__: (not defined)
```

```
FILE: level_7/factories/create_ensembling_method.py
  Module docstring: Factory for creating ensembling methods by name.
  Classes: (none)
  Functions:
    - create_ensembling_method(method_name: str, **kwargs) -> EnsemblingMethod
  Imports:
    - from layers.layer_0_core.level_0 import EnsemblingMethod [internal]
    - from layers.layer_0_core.level_3 import PerTargetWeightedEnsemble [internal]
    - from layers.layer_0_core.level_6 import (SimpleAverageEnsemble, WeightedAverageEnsemble, RankedAverageEnsemble, PercentileAverageEnsemble, TargetSpecificEnsemble) [internal]
  Line count: 37
  __all__: (not defined)
```

```
FILE: level_7/grid_search/__init__.py
  Module docstring: Grid search: hyperparameter base, variant builders, execution; results/cleanup from level_6.
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_0_core.level_6 import (auto_detect_grid_search_results, calculate_focused_grid_size, get_completed_count, run_final_cleanup, run_variant_cleanup) [internal]
    - from .dataset_variant_executor import run_single_variant [internal]
    - from .hyperparameter_base import HyperparameterGridSearchBase [internal]
    - from .variant_result_builders import build_error_result, build_success_result [internal]
  Line count: 22
  __all__: ["calculate_focused_grid_size", "auto_detect_grid_search_results", "build_success_result", "build_error_result", "HyperparameterGridSearchBase", "run_single_variant", "run_variant_cleanup", "run_final_cleanup", "get_completed_count"]
```

```
FILE: level_7/grid_search/dataset_variant_executor.py
  Module docstring: Variant execution for dataset grid search.
  Classes: (none)
  Functions:
    - _create_variant_config(config: Union[Any, Dict[str, Any]], preprocessing_list: List[str], augmentation_list: List[str], variant_model_dir: Path) -> Union[Any, Dict[str, Any]]
    - _extract_training_params(variant_config: Union[Any, Dict[str, Any]]) -> Tuple[str, Optional[str], int]
    - _create_variant_result(config: Union[Any, Dict[str, Any]], variant_index: int, variant_id: str, preprocessing_list: List[str], augmentation_list: List[str], batch_size_used: int, batch_size_reduced: bool, cv_score: Optional[float] = None, fold_scores: Optional[List[float]] = None, error: Optional[str] = None) -> Dict[str, Any]
    - run_single_variant(variant: Tuple[List[str], List[str]], variant_index: int, total_variants: int, config: Union[Any, Dict[str, Any]], train_csv_path: Path, base_model_dir: Path, device: Any, results_file: Path, train_pipeline_fn: Optional[Any] = None) -> Tuple[Optional[float], Optional[List[float]], Dict[str, Any], Path]
  Imports:
    - import copy [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Dict, List, Any, Tuple, Optional, Union [stdlib]
    - from layers.layer_0_core.level_0 import (ensure_dir, get_logger, ConfigValidationError, MODEL_DIR_DATASET_GRID_SEARCH, create_result_dict, create_error_result_dict) [internal]
    - from layers.layer_0_core.level_1 import cleanup_gpu_memory [internal]
    - from layers.layer_0_core.level_6 import create_variant_specific_data [internal]
  Line count: 224
  __all__: (not defined)
```

```
FILE: level_7/grid_search/hyperparameter_base.py
  Module docstring: Base class for hyperparameter grid searches; extends framework GridSearchBase.
  Classes:
    - HyperparameterGridSearchBase
        Methods:
          __init__(self, config: Any, grid_search_type: str, results_filename: str = 'results.json', quick_mode: bool = False, **kwargs)
          setup_parameter_grid(self, param_grid: Dict[str, List[Any]]) -> Tuple[Dict[str, List[Any]], List[tuple]]
          _generate_variant_grid(self) -> List[tuple]
          _create_variant_key_from_hyperparameters(self, variant: tuple) -> Tuple[Tuple[str, Any], ...]
  Functions: (none)
  Imports:
    - from abc import ABC [stdlib]
    - from typing import Dict, List, Any, Tuple [stdlib]
    - from itertools import product [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_6 import GridSearchBase [internal]
  Line count: 77
  __all__: (not defined)
```

```
FILE: level_7/grid_search/variant_result_builders.py
  Module docstring: Variant result builders for hyperparameter and regression grid search.
  Classes: (none)
  Functions:
    - build_success_result(variant_index: int, variant_id: str, cv_score: Optional[float], fold_scores: Optional[List[float]], batch_size_used: Optional[int], batch_size_reduced: bool, config: Any, hyperparameters: Dict[str, Any], feature_filename: Optional[str] = None, extra_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]
    - build_error_result(variant_index: int, variant_id: str, error: str, batch_size_used: int, batch_size_reduced: bool, config: Any, hyperparameters: Dict[str, Any], skipped: bool = False) -> Dict[str, Any]
  Imports:
    - from typing import Dict, Any, Optional, List [stdlib]
    - from layers.layer_0_core.level_0 import create_result_dict, create_error_result_dict [internal]
    - from layers.layer_0_core.level_6 import create_variant_specific_data [internal]
  Line count: 62
  __all__: (not defined)
```

## 3. __init__.py Public API Summary

```
INIT: level_7/__init__.py
  Exports: calculate_focused_grid_size, auto_detect_grid_search_results, build_success_result, build_error_result, create_ensembling_method, HyperparameterGridSearchBase, run_single_variant, create_tabular_model, run_variant_cleanup, run_final_cleanup, get_completed_count
  Re-exports from: level_7.factories, level_7.grid_search
```

```
INIT: level_7/factories/__init__.py
  Exports: create_tabular_model, create_ensembling_method
  Re-exports from: level_7.factories.create_ensembling_method, level_7.factories.tabular_model_factory
```

```
INIT: level_7/grid_search/__init__.py
  Exports: calculate_focused_grid_size, auto_detect_grid_search_results, build_success_result, build_error_result, HyperparameterGridSearchBase, run_single_variant, run_variant_cleanup, run_final_cleanup, get_completed_count
  Re-exports from: layers.layer_0_core.level_6, level_7.grid_search.dataset_variant_executor, level_7.grid_search.hyperparameter_base, level_7.grid_search.variant_result_builders
```

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0: ensure_dir, get_logger, ConfigValidationError, MODEL_DIR_DATASET_GRID_SEARCH, create_result_dict, create_error_result_dict, EnsemblingMethod
  From layers.layer_0_core.level_1: cleanup_gpu_memory
  From layers.layer_0_core.level_3: PerTargetWeightedEnsemble
  From layers.layer_0_core.level_5: BaseTabularModel
  From layers.layer_0_core.level_6: MLPModel, LogisticRegressionModel, RidgeModel, XGBoostModel, LightGBMModel, SimpleAverageEnsemble, WeightedAverageEnsemble, RankedAverageEnsemble, PercentileAverageEnsemble, TargetSpecificEnsemble, auto_detect_grid_search_results, calculate_focused_grid_size, get_completed_count, run_final_cleanup, run_variant_cleanup, create_variant_specific_data, GridSearchBase
  From same level (level_7) in logic files:
    relative `from .` / `from .module` — used in __init__.py and package inits only in subpackages; dataset_variant_executor and other logic use absolute layers.layer_0_core.* only (no relative in non-init logic files)
  From level_8 or higher: (none observed)
```

## 5. FLAGS

```
FLAGS:
  level_7/factories/__init__.py — 4 lines (minimal package surface)
  level_7/grid_search/dataset_variant_executor.py — 224 lines (largest module in level)
  Subpackage/filenames containing "helpers" pattern: (none at level_7; grid_search has executors/builders)
  Keywords (deprecated, legacy, compat, backwards, TODO: remove, shim): (none found)
  Duplicate public names across files in level_7: (none observed for classes; create_tabular_model / create_ensembling_method single-definition each)
```

## 6. Static scan summary (precheck)

- Source: `precheck_level_7_2026-04-08.md` under general summaries.
- `precheck_status`: skipped_machine_script (`ModuleNotFoundError: No module named 'torchvision'`).
- Machine Phase 7 reconciliation / devtools precheck stack did not run in the environment that produced the precheck artifact.
