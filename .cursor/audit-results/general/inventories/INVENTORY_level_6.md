---
generated: 2026-04-08
audit_scope: general
level_name: level_6
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
---

# INVENTORY: level_6

#### 1. Package & File Tree

```
level_6/
  README.md
  __init__.py
  ensembling/
    __init__.py
    README.md
    ensembling_methods.py
  grid_search/
    __init__.py
    README.md
    grid_search_base.py
    grid_search_results.py
    result_handlers.py
    variant_cleanup_runner.py
    variant_grid.py
  metadata/
    __init__.py
    combo_lookup.py
  prediction/
    __init__.py
    README.md
    create_test_dataloader.py
    predict_pipeline.py
  tabular/
    __init__.py
    README.md
    mlp_model.py
    tabular_predictor.py
    tabular_trainer.py
  tabular_models/
    __init__.py
    README.md
    linear.py
    tree.py
  vision/
    __init__.py
    README.md
    vision_model_registry.py
```

---

#### 2. Per-File Details

```
FILE: level_6/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import ensembling, grid_search, metadata, prediction, tabular, tabular_models, vision [relative]
    - from .ensembling import * [relative]
    - from .grid_search import * [relative]
    - from .metadata import * [relative]
    - from .prediction import * [relative]
    - from .tabular import * [relative]
    - from .tabular_models import * [relative]
    - from .vision import * [relative]
  Line count: 29
  __all__: tuple composition of subpackage __all__ lists
```

```
FILE: level_6/ensembling/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .ensembling_methods import PercentileAverageEnsemble, RankedAverageEnsemble, SimpleAverageEnsemble, TargetSpecificEnsemble, WeightedAverageEnsemble [relative]
  Line count: 17
  __all__: SimpleAverageEnsemble, WeightedAverageEnsemble, RankedAverageEnsemble, PercentileAverageEnsemble, TargetSpecificEnsemble
```

```
FILE: level_6/ensembling/ensembling_methods.py
  Classes:
    - SimpleAverageEnsemble — Methods: combine(self, predictions_list: List[np.ndarray], weights: Optional[List[float]]=None) -> np.ndarray; get_name(self) -> str
    - WeightedAverageEnsemble — Methods: combine(self, predictions_list: List[np.ndarray], weights: List[float]) -> np.ndarray; get_name(self) -> str
    - RankedAverageEnsemble — Methods: combine(self, predictions_list: List[np.ndarray], weights: List[float]) -> np.ndarray; get_name(self) -> str
    - PercentileAverageEnsemble — Methods: combine(self, predictions_list: List[np.ndarray], weights: List[float]) -> np.ndarray; get_name(self) -> str
    - TargetSpecificEnsemble — Methods: __init__(self, target_selection: Dict[str, int], target_names: Optional[List[str]]=None, base_method: Optional[EnsemblingMethod]=None); combine(self, predictions_list: List[np.ndarray], weights: Optional[List[float]]=None) -> np.ndarray; get_name(self) -> str
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from typing import Dict, List, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, EnsemblingMethod, calculate_percentile_weights [internal]
    - from layers.layer_0_core.level_1 import validate_predictions_for_ensemble [internal]
    - from layers.layer_0_core.level_2 import simple_average, model_rank_weights [internal]
    - from layers.layer_0_core.level_5 import combine_with_fallback [internal]
  Line count: 240
  __all__: (none)
```

```
FILE: level_6/grid_search/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_0_core.level_5 import analyze_results_for_focused_grid, cleanup_checkpoints, cleanup_grid_search_checkpoints_retroactive, extract_parameter_ranges, extract_top_results, get_focused_parameter_grid, get_next_variant_index, load_completed_variants_helper, load_raw_results, save_variant_result_helper [internal]
    - from .grid_search_base import GridSearchBase [relative]
    - from .grid_search_results import auto_detect_grid_search_results, calculate_focused_grid_size [relative]
    - from .result_handlers import handle_dataset_grid_search_result, handle_hyperparameter_grid_search_result, handle_regression_grid_search_result [relative]
    - from .variant_cleanup_runner import get_completed_count, run_final_cleanup, run_variant_cleanup [relative]
    - from .variant_grid import create_regression_variant_key_from_result, create_variant_key, create_variant_key_from_result, create_variant_specific_data, get_default_hyperparameters [relative]
  Line count: 56
  __all__: GridSearchBase, auto_detect_grid_search_results, calculate_focused_grid_size, get_completed_count, run_final_cleanup, run_variant_cleanup, handle_hyperparameter_grid_search_result, handle_dataset_grid_search_result, handle_regression_grid_search_result, get_focused_parameter_grid, load_raw_results, extract_top_results, extract_parameter_ranges, analyze_results_for_focused_grid, create_variant_specific_data, create_variant_key, create_variant_key_from_result, create_regression_variant_key_from_result, get_default_hyperparameters, cleanup_grid_search_checkpoints_retroactive, cleanup_checkpoints, load_completed_variants_helper, get_next_variant_index, save_variant_result_helper
```

```
FILE: level_6/grid_search/grid_search_base.py
  Classes:
    - GridSearchBase
        Methods: __init__(self, config: Any, grid_search_type: str, results_filename: str='results.json', quick_mode: bool=False, ontology: Optional[str]=None, **kwargs)
                 setup(self) -> None
                 execute(self) -> Dict[str, Any]
                 get_param_grid(self, grid_config: Dict[str, Any], model_type: Optional[str]=None) -> Dict[str, List]
                 _generate_variant_grid(self) -> List[Any]
                 _create_variant_key(self, variant: Any) -> Any
                 _run_variant(self, variant: Any, variant_index: int) -> Dict[str, Any]
                 _load_results(self) -> None
                 _save_results(self) -> None
                 _save_checkpoint(self) -> None
                 _load_checkpoint(self) -> bool
                 cleanup(self) -> None
  Functions:
    - _filter_param_grid(grid_config: Dict[str, Any], quick_mode: bool=False, ontology: Optional[str]=None, model_type: Optional[str]=None) -> Dict[str, List]
  Imports:
    - from abc import ABC, abstractmethod [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Optional, Set [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger [internal]
    - from layers.layer_0_core.level_1 import BasePipeline, execute_variants [internal]
    - from layers.layer_0_core.level_5 import load_results, save_results, load_checkpoint, save_checkpoint [internal]
  Line count: 265
  __all__: (none)
```

```
FILE: level_6/grid_search/grid_search_results.py
  Classes: (none)
  Functions:
    - calculate_focused_grid_size(base_search_type: str, previous_results_file: str, top_n_results: int=10, range_expansion_factor: float=1.5, min_values_per_param: int=2) -> Tuple[Dict[str, List[Any]], int, Optional[int]]
    - auto_detect_grid_search_results(model_name: Optional[str]=None) -> str
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import calculate_total_combinations, get_logger, is_kaggle [internal]
    - from layers.layer_0_core.level_1 import get_transformer_hyperparameter_grid, resolve_environment_path [internal]
    - from layers.layer_0_core.level_5 import get_focused_parameter_grid [internal]
  Line count: 110
  __all__: (none)
```

```
FILE: level_6/grid_search/result_handlers.py
  Classes: (none)
  Functions:
    - _handle_grid_search_returncode(returncode: int, stdout_lines: List[str], log_file: str, error_prefix: str) -> None
    - _log_grid_search_success(log_success_fn: Callable[[], None]) -> None
    - handle_hyperparameter_grid_search_result(returncode: int, stdout_lines: List[str], log_file: str) -> None
    - handle_dataset_grid_search_result(returncode: int, stdout_lines: List[str], log_file: str, dataset_type: Optional[str]=None) -> None
    - handle_regression_grid_search_result(regression_model_type: str, results_file: Optional[str]=None) -> Dict[str, Any]
  Imports:
    - from typing import List, Optional, Dict, Any, Callable [stdlib]
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import resolve_environment_path [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
    - from layers.layer_0_core.level_5 import get_writable_metadata_dir [internal]
  Line count: 171
  __all__: (none)
```

```
FILE: level_6/grid_search/variant_cleanup_runner.py
  Classes: (none)
  Functions:
    - _get_cleanup_config(config: Union[Any, Dict[str, Any]]) -> Tuple[bool, int, int, bool]
    - run_variant_cleanup(config: Union[Any, Dict[str, Any]], base_model_dir: Path, results_file: Path, variant_model_dir: Path, cv_score: Optional[float], variant_id: str) -> None
    - delete_variant_checkpoints_immediately(config: Union[Any, Dict[str, Any]], variant_model_dir: Path, cv_score: Optional[float], variant_id: str) -> None
    - cleanup_top_variants(config: Union[Any, Dict[str, Any]], base_model_dir: Path, results_file: Path, cv_score: Optional[float]) -> None
    - run_periodic_cleanup(config: Union[Any, Dict[str, Any]], base_model_dir: Path, results_file: Path, completed_count: int) -> None
    - get_completed_count(results_file: Path) -> int
    - run_final_cleanup(config: Union[Any, Dict[str, Any]], base_model_dir: Path, results_file: Optional[Path]) -> None
  Imports:
    - import shutil [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import extract_results_list, get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
    - from layers.layer_0_core.level_5 import cleanup_grid_search_checkpoints_retroactive [internal]
  Line count: 223
  __all__: (none)
```

```
FILE: level_6/grid_search/variant_grid.py
  Classes: (none)
  Functions:
    - get_default_hyperparameters() -> Dict[str, Any]
    - _extract_dataset_type(config: Union[Any, Dict[str, Any]]) -> str
    - create_variant_specific_data(config: Union[Any, Dict[str, Any]], preprocessing_list: Optional[List[str]]=None, augmentation_list: Optional[List[str]]=None, hyperparameters: Optional[Dict[str, Any]]=None, feature_filename: Optional[str]=None, metadata_dir: Optional[Path]=None) -> Dict[str, Any]
    - create_variant_key(config: Union[Any, Dict[str, Any]], preprocessing_list: List[str], augmentation_list: List[str], hyperparameters: Dict[str, Any]) -> Tuple[str, Tuple[str, ...], Tuple[str, ...], Tuple[Tuple[str, Any], ...]]
    - create_variant_key_from_result(result: Dict[str, Any], config: Optional[Union[Any, Dict[str, Any]]]=None) -> Optional[Tuple[str, Tuple[str, ...], Tuple[str, ...], Tuple[Tuple[str, Any], ...]]]
    - create_regression_variant_key_from_result(result: Dict[str, Any]) -> Optional[Tuple[str, Tuple[Tuple[str, Any], ...]]]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Dict, List, Any, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import DATASET_TYPE_SPLIT, get_logger [internal]
    - from layers.layer_0_core.level_1 import get_transformer_hyperparameter_grid [internal]
    - from layers.layer_0_core.level_5 import find_metadata_dir [internal]
  Line count: 160
  __all__: (none)
```

```
FILE: level_6/metadata/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .combo_lookup import find_combo_id_from_config [relative]
  Line count: 8
  __all__: ["find_combo_id_from_config"]
```

```
FILE: level_6/metadata/combo_lookup.py
  Classes: (none)
  Functions:
    - find_combo_id_from_config(config: Any) -> Optional[str]
  Imports:
    - from typing import Any, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json_raw [internal]
    - from layers.layer_0_core.level_5 import find_metadata_dir [internal]
  Line count: 30
  __all__: (none)
```

```
FILE: level_6/prediction/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .create_test_dataloader import create_test_dataloader [relative]
    - from .predict_pipeline import PredictPipeline [relative]
  Line count: 9
  __all__: PredictPipeline, create_test_dataloader
```

```
FILE: level_6/prediction/create_test_dataloader.py
  Classes: (none)
  Functions:
    - create_test_dataloader(test_csv_path: str, data_root: str, image_path_column: str, primary_targets: List[str], image_size: Tuple[int, int], batch_size: int=32, dataset_type: str='split', num_workers: int=0)
  Imports:
    - from typing import List, Tuple [stdlib]
    - from layers.layer_0_core.level_2 import build_preprocessing_transforms, create_dataloader_from_dataset, create_streaming_dataset_for_test [internal]
    - from layers.layer_0_core.level_5 import load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets [internal]
  Line count: 47
  __all__: (none)
```

```
FILE: level_6/prediction/predict_pipeline.py
  Classes:
    - PredictPipeline
        Methods: __init__(self, config: Any, model_path: str, model_type: str='vision', use_tta: bool=False, **kwargs)
                 setup(self) -> None
                 execute(self) -> Dict[str, Any]
                 _predict_vision(self) -> Dict[str, Any]
                 _predict_tabular(self) -> Dict[str, Any]
                 cleanup(self) -> None
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from typing import Dict, Any [stdlib]
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch [internal]
    - from layers.layer_0_core.level_1 import validate_config_section_exists, BasePipeline, get_device [internal]
    - from layers.layer_0_core.level_2 import VisionPredictor [internal]
    - from layers.layer_0_core.level_3 import TTAPredictor [internal]
    - from layers.layer_0_core.level_4 import create_test_dataloader, create_vision_model, load_pickle [internal]
  Line count: 173
  __all__: (none)
```

```
FILE: level_6/tabular/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .mlp_model import MLPModel [relative]
    - from .tabular_predictor import TabularPredictor [relative]
    - from .tabular_trainer import TabularTrainer [relative]
  Line count: 11
  __all__: TabularTrainer, TabularPredictor, MLPModel
```

```
FILE: level_6/tabular/mlp_model.py
  Classes:
    - _MLPNetwork — Methods: __init__(self, input_dim: int, output_dim: int, hidden_dims: list=None, dropout_rate: float=0.3, use_batch_norm: bool=True); forward(self, x)
    - MLPModel — Methods: __init__(self, input_dim: int, output_dim: int, hidden_dims: list=None, dropout_rate: float=0.3, learning_rate: float=0.001, batch_size: int=32, num_epochs: int=10, use_batch_norm: bool=True, device: str='auto', sparse_loss_class=None, **kwargs); fit(self, X: np.ndarray, y: np.ndarray, validation_split: float=0.1, **kwargs) -> 'MLPModel'; predict(self, X: np.ndarray, threshold: float=0.5, **kwargs) -> np.ndarray; predict_proba(self, X: np.ndarray) -> np.ndarray; save(self, path: str) -> None; load(self, path: str) -> 'MLPModel'
  Functions:
    - _create_training_datasets(X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, output_dim: int, sparse_loss_class: Optional[Any]=None) -> Tuple[Any, Any, Any]
  Imports:
    - import numpy [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Any, Optional, Tuple [stdlib]
    - from scipy.sparse import csr_matrix, issparse [third_party]
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal]
    - from layers.layer_0_core.level_1 import TabularDataset, get_device [internal]
    - from layers.layer_0_core.level_2 import run_train_epoch, run_validate_epoch, validate_array [internal]
    - from layers.layer_0_core.level_5 import BaseTabularModel, SparseTabularDataset [internal]
  Line count: 251
  __all__: (none)
```

```
FILE: level_6/tabular/tabular_predictor.py
  Classes:
    - TabularPredictor
        Methods: __init__(self, model: BaseTabularModel, threshold: float=0.5)
                 predict(self, X: Union[np.ndarray, pd.DataFrame], threshold: Optional[float]=None) -> np.ndarray
                 predict_proba(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - import pandas [third_party]
    - from typing import Union, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_5 import BaseTabularModel [internal]
  Line count: 75
  __all__: (none)
```

```
FILE: level_6/tabular/tabular_trainer.py
  Classes:
    - TabularTrainer
        Methods: __init__(self, model: BaseTabularModel, validation_split: float=0.0, random_state: int=42)
                 fit(self, X: Union[np.ndarray, pd.DataFrame], y: Union[np.ndarray, pd.Series], **kwargs) -> Dict[str, Any]
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - import pandas [third_party]
    - from typing import Dict, Any, Union, List [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import get_train_test_split [internal]
    - from layers.layer_0_core.level_4 import calculate_metrics [internal]
    - from layers.layer_0_core.level_5 import BaseTabularModel [internal]
  Line count: 77
  __all__: (none)
```

```
FILE: level_6/tabular_models/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .linear import LogisticRegressionModel, RidgeModel [relative]
    - from .tree import XGBoostModel, LightGBMModel [relative]
  Line count: 15
  __all__: LogisticRegressionModel, RidgeModel, XGBoostModel, LightGBMModel
```

```
FILE: level_6/tabular_models/linear.py
  Classes:
    - LogisticRegressionModel — Methods: __init__(self, **kwargs); fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'LogisticRegressionModel'; predict_proba(self, X: np.ndarray) -> np.ndarray; save(self, path: str) -> None; load(self, path: str) -> 'LogisticRegressionModel'
    - RidgeModel — Methods: __init__(self, **kwargs); fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'RidgeModel'; predict_proba(self, X: np.ndarray) -> np.ndarray; save(self, path: str) -> None; load(self, path: str) -> 'RidgeModel'
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import get_logistic_regression, get_ridge_classifier [internal]
    - from layers.layer_0_core.level_5 import BaseTabularModel [internal]
  Line count: 86
  __all__: (none)
```

```
FILE: level_6/tabular_models/tree.py
  Classes:
    - XGBoostModel — Methods: __init__(self, **kwargs); fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'XGBoostModel'; predict_proba(self, X: np.ndarray) -> np.ndarray; save(self, path: str) -> None; load(self, path: str) -> 'XGBoostModel'
    - LightGBMModel — Methods: __init__(self, **kwargs); fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'LightGBMModel'; predict_proba(self, X: np.ndarray) -> np.ndarray; save(self, path: str) -> None; load(self, path: str) -> 'LightGBMModel'
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import get_lgbm_classifier, get_xgb_classifier [internal]
    - from layers.layer_0_core.level_5 import BaseTabularModel [internal]
  Line count: 85
  __all__: (none)
```

```
FILE: level_6/vision/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .vision_model_registry import get_vision_model_config, list_vision_models [relative]
  Line count: 8
  __all__: get_vision_model_config, list_vision_models
```

```
FILE: level_6/vision/vision_model_registry.py
  Classes: (none)
  Functions:
    - get_vision_model_config(model_name: str)
    - list_vision_models()
    - __getattr__(name: str)
  Imports:
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_5 import create_json_model_registry [internal]
  Line count: 29
  __all__: (none)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_6/__init__.py
  Exports: combined __all__ from ensembling, grid_search, metadata, prediction, tabular, tabular_models, vision
  Re-exports from: those subpackages
```

```
INIT: level_6/ensembling/__init__.py — Exports: SimpleAverageEnsemble, WeightedAverageEnsemble, RankedAverageEnsemble, PercentileAverageEnsemble, TargetSpecificEnsemble
INIT: level_6/grid_search/__init__.py — Exports: long combined list (see §2)
INIT: level_6/metadata/__init__.py — Exports: find_combo_id_from_config
INIT: level_6/prediction/__init__.py — Exports: PredictPipeline, create_test_dataloader
INIT: level_6/tabular/__init__.py — Exports: TabularTrainer, TabularPredictor, MLPModel
INIT: level_6/tabular_models/__init__.py — Exports: LogisticRegressionModel, RidgeModel, XGBoostModel, LightGBMModel
INIT: level_6/vision/__init__.py — Exports: get_vision_model_config, list_vision_models
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  Logic modules use `from layers.layer_0_core.level_K import ...` with K ∈ {0,1,2,3,4,5} only; no imports from level_6 observed in non-init logic files.
  From level_5 (representative): combine_with_fallback, load_results, save_results, load_checkpoint, save_checkpoint, get_focused_parameter_grid, get_writable_metadata_dir, cleanup_grid_search_checkpoints_retroactive, find_metadata_dir, create_json_model_registry, BaseTabularModel, SparseTabularDataset, load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets
  From level_4: load_json, load_json_raw, create_test_dataloader, create_vision_model, load_pickle, calculate_metrics
  From level_3: TTAPredictor
  From level_2: VisionPredictor, build_preprocessing_transforms, create_dataloader_from_dataset, create_streaming_dataset_for_test, get_train_test_split, simple_average, model_rank_weights, run_train_epoch, run_validate_epoch, validate_array, get_logistic_regression, get_ridge_classifier, get_lgbm_classifier, get_xgb_classifier
  From level_1: validate_config_section_exists, BasePipeline, get_device, validate_predictions_for_ensemble, get_transformer_hyperparameter_grid, resolve_environment_path, execute_variants, TabularDataset
  From level_0: get_logger, ensure_dir, get_torch, EnsemblingMethod, calculate_percentile_weights, DATASET_TYPE_SPLIT, extract_results_list, calculate_total_combinations, is_kaggle
  Same-level (level_6) in logic files: none
  From level_7+: none observed
  Relative imports: __init__ and grid_search local modules only
```

---

#### 5. Flags

```
FLAGS:
  level_6/grid_search/__init__.py — imports many symbols from level_5 in barrel (large public surface re-export)
  level_6/prediction/predict_pipeline.py — imports `create_test_dataloader` from `layers.layer_0_core.level_4` while `level_6/prediction/create_test_dataloader.py` defines a separate `create_test_dataloader` (duplicate symbol name, different implementations/modules)
  level_6/metadata/combo_lookup.py — 30 lines (small)
  level_6/vision/vision_model_registry.py — 29 lines (small); module-level __getattr__
```

---

#### 6. Static scan summary (optional)

- Precheck artifact reports **precheck_status: skipped_machine_script** (**ModuleNotFoundError: No module named 'torchvision'**); no machine violation list merged.

**Machine-generated (verify):** none (`inventory_bootstrap_path` not provided).
