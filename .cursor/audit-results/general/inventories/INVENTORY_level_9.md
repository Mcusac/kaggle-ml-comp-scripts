---
generated: 2026-04-08
audit_scope: general
level_name: level_9
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_9_2026-04-08.md
---

# INVENTORY: level_9

## 1. Package & File Tree

```
level_9/
  README.md
  __init__.py
  grid_search/
    README.md
    __init__.py
    dataset_grid_search_pipeline.py
    hyperparameter.py
    regression_grid_search.py
  training/
    README.md
    __init__.py
    cross_validate.py
    train_and_export.py
  train_predict/
    README.md
    __init__.py
    workflow.py
```

## 2. Per-File Details

```
FILE: level_9/__init__.py
  Module docstring: Level 9: Hyperparameter grid search, train-then-predict workflow.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .training import CrossValidateWorkflow, TrainAndExportWorkflow [internal]
    - from .grid_search import (HyperparameterGridSearch, RegressionGridSearch, attach_paths_to_config, dataset_grid_search_pipeline, regression_grid_search_pipeline, test_max_augmentation_pipeline) [internal]
    - from .train_predict import TrainPredictWorkflow [internal]
  Line count: 22
  __all__: ["CrossValidateWorkflow", "TrainAndExportWorkflow", "attach_paths_to_config", "dataset_grid_search_pipeline", "HyperparameterGridSearch", "RegressionGridSearch", "regression_grid_search_pipeline", "test_max_augmentation_pipeline", "TrainPredictWorkflow"]
```

```
FILE: level_9/grid_search/__init__.py
  Module docstring: Grid search pipelines: dataset, regression, and hyperparameter variants.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .dataset_grid_search_pipeline import attach_paths_to_config, dataset_grid_search_pipeline, test_max_augmentation_pipeline [internal]
    - from .hyperparameter import HyperparameterGridSearch [internal]
    - from .regression_grid_search import RegressionGridSearch, regression_grid_search_pipeline [internal]
  Line count: 16
  __all__: ["attach_paths_to_config", "dataset_grid_search_pipeline", "test_max_augmentation_pipeline", "HyperparameterGridSearch", "RegressionGridSearch", "regression_grid_search_pipeline"]
```

```
FILE: level_9/grid_search/dataset_grid_search_pipeline.py
  Module docstring: Dataset grid search pipeline. Requires contest_context from contest layer (orchestration does not import contest).
  Classes:
    - SimplePaths
        Methods:
          __init__(self, paths_obj: Any) -> None
          get_output_dir(self) -> str
          get_models_base_dir(self) -> str
          get_data_root(self) -> Optional[str]
  Functions:
    - attach_paths_to_config(config: Any, paths: Any) -> None
    - dataset_grid_search_pipeline(contest_context: Any, train_pipeline_fn: Optional[Any] = None, config: Optional[Union[Any, Dict[str, Any]]] = None, data_root: Optional[str] = None, **kwargs) -> None
    - test_max_augmentation_pipeline(contest_context: Any, preprocessing_list: Optional[list] = None, augmentation_list: Optional[list] = None, config: Optional[Union[Any, Dict[str, Any]]] = None, data_root: Optional[str] = None, **kwargs) -> None
  Imports:
    - from typing import Optional, Union, Dict, Any [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, BEST_VARIANT_FILE_DATASET, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION [internal]
    - from layers.layer_0_core.level_4 import save_json [internal]
    - from layers.layer_0_core.level_8 import DatasetGridSearch [internal]
  Line count: 116
  __all__: (not defined)
```

```
FILE: level_9/grid_search/hyperparameter.py
  Module docstring: Hyperparameter grid search.
  Classes:
    - HyperparameterGridSearch
        Methods:
          __init__(self, config: Any, param_grid: Dict[str, List[Any]], model_type: str = 'vision', **kwargs)
          setup(self) -> None
          _generate_variant_grid(self) -> List[Tuple]
          _create_variant_key(self, variant: Tuple) -> Tuple
          _run_variant(self, variant: Tuple, variant_index: int) -> Dict[str, Any]
          _apply_hyperparameters(self, hyperparameters: Dict[str, Any]) -> Any
  Functions: (none)
  Imports:
    - import copy [stdlib]
    - from typing import Dict, List, Any, Tuple [stdlib]
    - from itertools import product [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger [internal]
    - from layers.layer_0_core.level_4 import EvaluatePipeline [internal]
    - from layers.layer_0_core.level_6 import GridSearchBase, PredictPipeline [internal]
    - from layers.layer_0_core.level_8 import TrainPipeline [internal]
  Line count: 150
  __all__: (not defined)
```

```
FILE: level_9/grid_search/regression_grid_search.py
  Module docstring: Regression head hyperparameter grid search pipeline.
  Classes:
    - RegressionGridSearch
        Methods:
          __init__(self, config: Union[Any, Dict[str, Any]], regression_model_type: str, metadata_handler: Optional[Any] = None, metric_calculator: Optional[Any] = None, **kwargs)
          setup_features(self, all_features: Any, all_targets: Any, fold_assignments: Any, feature_filename: str, param_names: List[str], param_grid: Dict[str, List[Any]]) -> None
          _get_grid_search_type(self) -> str
          _get_results_filename(self) -> str
          _create_variant_key(self, variant: tuple) -> Tuple
          _create_variant_key_from_result(self, result: Dict[str, Any]) -> Optional[Tuple]
          _run_variant(self, variant: tuple, variant_index: int, **kwargs) -> Dict[str, Any]
  Functions:
    - regression_grid_search_pipeline(contest_context: Any, config: Optional[Union[Any, Dict[str, Any]]] = None, feature_filename: Optional[str] = None, regression_model_type: Optional[str] = None, search_type: str = 'quick', **kwargs) -> None
  Imports:
    - import numpy as np [third-party]
    - from typing import Optional, Union, Dict, Any, Tuple, List [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, create_error_result_dict [internal]
    - from layers.layer_0_core.level_6 import create_variant_specific_data, create_regression_variant_key_from_result [internal]
    - from layers.layer_0_core.level_7 import HyperparameterGridSearchBase [internal]
    - from layers.layer_0_core.level_8 import run_regression_cv_fold, create_regression_variant_result [internal]
  Line count: 230
  __all__: (not defined)
```

```
FILE: level_9/training/__init__.py
  Module docstring: Training workflows composed above level_8.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .cross_validate import CrossValidateWorkflow [internal]
    - from .train_and_export import TrainAndExportWorkflow [internal]
  Line count: 4
  __all__: ["CrossValidateWorkflow", "TrainAndExportWorkflow"]
```

```
FILE: level_9/training/cross_validate.py
  Module docstring: Cross-validation workflow.
  Classes:
    - CrossValidateWorkflow
        Methods:
          __init__(self, config: Any, model_type: str = 'vision', n_folds: int = 5, shuffle: bool = True, random_state: int = 42, primary_metric_key: Optional[str] = None, **kwargs)
          setup(self) -> None
          execute(self) -> Dict[str, Any]
          _cv_vision(self) -> Dict[str, Any]
          _aggregate_cv_results(self, fold_scores: List[float]) -> Dict[str, Any]
          _cv_tabular(self) -> Dict[str, Any]
          cleanup(self) -> None
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from typing import Dict, Any, List, Optional [stdlib]
    - from pathlib import Path [stdlib]
    - from sklearn.model_selection import KFold, StratifiedKFold [third-party]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import BasePipeline [internal]
    - from layers.layer_0_core.level_4 import EvaluatePipeline [internal]
    - from layers.layer_0_core.level_6 import PredictPipeline [internal]
    - from layers.layer_0_core.level_8 import TrainPipeline [internal]
  Line count: 192
  __all__: (not defined)
```

```
FILE: level_9/training/train_and_export.py
  Module docstring: Train and export workflow.
  Classes:
    - TrainAndExportWorkflow
        Methods:
          __init__(self, config: Any, model_type: str = 'vision', export_dir: Optional[str] = None, **kwargs)
          setup(self) -> None
          execute(self) -> Dict[str, Any]
          cleanup(self) -> None
  Functions: (none)
  Imports:
    - from typing import Dict, Any, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import BasePipeline [internal]
    - from layers.layer_0_core.level_5 import ExportPipeline [internal]
    - from layers.layer_0_core.level_8 import TrainPipeline [internal]
  Line count: 92
  __all__: (not defined)
```

```
FILE: level_9/train_predict/__init__.py
  Module docstring: Train-then-predict workflow.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .workflow import TrainPredictWorkflow [internal]
  Line count: 3
  __all__: ["TrainPredictWorkflow"]
```

```
FILE: level_9/train_predict/workflow.py
  Module docstring: Train then predict workflow.
  Classes:
    - TrainPredictWorkflow
        Methods:
          __init__(self, config: Any, model_type: str = 'vision', use_tta: bool = False, **kwargs)
          setup(self) -> None
          execute(self) -> Dict[str, Any]
          cleanup(self) -> None
  Functions: (none)
  Imports:
    - from typing import Dict, Any [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import BasePipeline [internal]
    - from layers.layer_0_core.level_6 import PredictPipeline [internal]
    - from layers.layer_0_core.level_8 import TrainPipeline [internal]
  Line count: 94
  __all__: (not defined)
```

## 3. __init__.py Public API Summary

```
INIT: level_9/__init__.py
  Exports: CrossValidateWorkflow, TrainAndExportWorkflow, attach_paths_to_config, dataset_grid_search_pipeline, HyperparameterGridSearch, RegressionGridSearch, regression_grid_search_pipeline, test_max_augmentation_pipeline, TrainPredictWorkflow
  Re-exports from: level_9.training, level_9.grid_search, level_9.train_predict
```

```
INIT: level_9/grid_search/__init__.py
  Exports: attach_paths_to_config, dataset_grid_search_pipeline, test_max_augmentation_pipeline, HyperparameterGridSearch, RegressionGridSearch, regression_grid_search_pipeline
  Re-exports from: level_9.grid_search.dataset_grid_search_pipeline, level_9.grid_search.hyperparameter, level_9.grid_search.regression_grid_search
```

```
INIT: level_9/training/__init__.py
  Exports: CrossValidateWorkflow, TrainAndExportWorkflow
  Re-exports from: level_9.training.cross_validate, level_9.training.train_and_export
```

```
INIT: level_9/train_predict/__init__.py
  Exports: TrainPredictWorkflow
  Re-exports from: level_9.train_predict.workflow
```

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0: get_logger, BEST_VARIANT_FILE_DATASET, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION, ensure_dir, create_error_result_dict
  From layers.layer_0_core.level_1: BasePipeline
  From layers.layer_0_core.level_4: save_json, EvaluatePipeline
  From layers.layer_0_core.level_5: ExportPipeline
  From layers.layer_0_core.level_6: GridSearchBase, PredictPipeline, create_variant_specific_data, create_regression_variant_key_from_result
  From layers.layer_0_core.level_7: HyperparameterGridSearchBase
  From layers.layer_0_core.level_8: DatasetGridSearch, TrainPipeline, run_regression_cv_fold, create_regression_variant_result
  From same level (level_9): relative imports in __init__ files and subpackages only
  From level_10 or higher: (none observed)
```

## 5. FLAGS

```
FLAGS:
  level_9/training/__init__.py — 4 lines (minimal)
  level_9/train_predict/__init__.py — 3 lines (minimal)
  level_9/grid_search/regression_grid_search.py — 230 lines (largest module in level)
  level_9/training/cross_validate.py — 192 lines
  Dataset pipeline defines unused parameters in signatures: dataset_grid_search_pipeline (`data_root`), test_max_augmentation_pipeline (`data_root`) — observational
  Keywords (deprecated, legacy, compat, backwards, TODO: remove, shim): (none found)
  Catch-all package dir names (utils/helpers/misc/common): (none); filenames include `workflow`, `pipeline` patterns
```

## 6. Static scan summary (precheck)

- Source: `precheck_level_9_2026-04-08.md` under general summaries.
- `precheck_status`: skipped_machine_script (`ModuleNotFoundError: No module named 'torchvision'`).
- Machine Phase 7 reconciliation / devtools precheck stack did not run in the environment that produced the precheck artifact.
