---
generated: 2026-04-08
audit_scope: general
level_name: level_5
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
---

# INVENTORY: level_5

#### 1. Package & File Tree

```
level_5/
  README.md
  __init__.py
  batch_loading/
    __init__.py
    README.md
    csv_batch.py
    image_batch.py
  data_structure/
    __init__.py
    README.md
    base/
      __init__.py
      README.md
      config_loader.py
      json_model_registry.py
    tabular/
      __init__.py
      README.md
      base.py
      sparse_tabular_dataset.py
  datasets/
    __init__.py
    README.md
    load_and_validate_test_data.py
    prepare_test_dataframe.py
    splits.py
    variants.py
  ensembling/
    __init__.py
    README.md
    combine.py
    stacking_ensemble.py
  export/
    __init__.py
    README.md
    export_pipeline.py
    operations.py
  file_io/
    __init__.py
    README.md
    merge.py
    submission.py
  grid_search/
    __init__.py
    README.md
    checkpoint_cleanup.py
    result_analysis.py
    results_persistence.py
    variant_tracking.py
  metadata/
    __init__.py
    README.md
    paths.py
    scores.py
  model_io/
    __init__.py
    README.md
    model_io.py
    model_saver_helper.py
  training/
    __init__.py
    README.md
    base_model_trainer.py
    vision_trainer.py
```

---

#### 2. Per-File Details

```
FILE: level_5/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import batch_loading, data_structure, datasets, ensembling, export, file_io, grid_search, metadata, model_io, training [relative]
    - from .batch_loading import * [relative]
    - from .data_structure import * [relative]
    - from .datasets import * [relative]
    - from .ensembling import * [relative]
    - from .export import * [relative]
    - from .file_io import * [relative]
    - from .grid_search import * [relative]
    - from .metadata import * [relative]
    - from .model_io import * [relative]
    - from .training import * [relative]
  Line count: 36
  __all__: tuple composition of subpackage __all__ lists
```

```
FILE: level_5/batch_loading/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .csv_batch import load_csv_batch [relative]
    - from .image_batch import load_image_batch [relative]
  Line count: 9
  __all__: ["load_csv_batch", "load_image_batch"]
```

```
FILE: level_5/batch_loading/csv_batch.py
  Classes: (none)
  Functions:
    - load_csv_batch(paths: Iterable[Union[str, Path]], *, show_progress: bool=False, **kwargs) -> List[pd.DataFrame]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Iterable, List, Union [stdlib]
    - import pandas [third_party]
    - from layers.layer_0_core.level_1 import load_batch [internal]
    - from layers.layer_0_core.level_4 import load_csv [internal]
  Line count: 52
  __all__: (none)
```

```
FILE: level_5/batch_loading/image_batch.py
  Classes: (none)
  Functions:
    - load_image_batch(paths: Iterable[Union[str, Path]], *, convert_rgb: bool=True, show_progress: bool=False) -> List[Image.Image]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Iterable, List, Union [stdlib]
    - from PIL import Image [third_party]
    - from layers.layer_0_core.level_1 import load_batch [internal]
    - from layers.layer_0_core.level_4 import load_image [internal]
  Line count: 52
  __all__: (none)
```

```
FILE: level_5/data_structure/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import base, tabular [relative]
    - from .base import * [relative]
    - from .tabular import * [relative]
  Line count: 10
  __all__: list(base.__all__) + list(tabular.__all__)
```

```
FILE: level_5/data_structure/base/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .config_loader import JSONConfigLoader [relative]
    - from .json_model_registry import create_json_model_registry [relative]
  Line count: 9
  __all__: ["JSONConfigLoader", "create_json_model_registry"]
```

```
FILE: level_5/data_structure/base/config_loader.py
  Classes:
    - JSONConfigLoader
        Methods: __init__(self, config_name: str, config_dir: str='config', lowercase_keys: bool=True)
                 _load(self) -> None
                 get(self, key: str) -> Optional[Any]
                 keys(self) -> List[str]
                 all(self) -> Dict[str, Any]
                 reload(self) -> None
  Functions: (none)
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Dict, Any, Optional, List [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 114
  __all__: (none)
```

```
FILE: level_5/data_structure/base/json_model_registry.py
  Classes: (none)
  Functions:
    - create_json_model_registry(config_path: Path) -> tuple[Callable[[str], Dict[str, Any]], Callable[[], List[str]], Callable[[], Dict[str, Any]]]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Callable, Dict, List [stdlib]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 94
  __all__: (none)
```

```
FILE: level_5/data_structure/tabular/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .base import BaseTabularModel [relative]
    - from .sparse_tabular_dataset import SparseTabularDataset [relative]
  Line count: 9
  __all__: ["BaseTabularModel", "SparseTabularDataset"]
```

```
FILE: level_5/data_structure/tabular/base.py
  Classes:
    - BaseTabularModel
        Methods: __init__(self, model_type: str, **kwargs)
                 fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> 'BaseTabularModel'
                 predict(self, X: np.ndarray, threshold: float=0.5, **kwargs) -> np.ndarray
                 predict_proba(self, X: np.ndarray) -> np.ndarray
                 save(self, path: str) -> None
                 load(self, path: str) -> 'BaseTabularModel'
                 _save_with_pickle(self, path: str, model_data: Dict[str, Any], model_name: str) -> None
                 _load_from_pickle(self, path: str, model_name: str) -> Dict[str, Any]
                 get_params(self) -> Dict[str, Any]
                 set_params(self, **params) -> 'BaseTabularModel'
  Functions: (none)
  Imports:
    - from abc import ABC, abstractmethod [stdlib]
    - from typing import Dict, Any [stdlib]
    - import numpy [third_party]
    - from layers.layer_0_core.level_0 import get_logger, ensure_file_dir [internal]
    - from layers.layer_0_core.level_4 import save_pickle, load_pickle [internal]
  Line count: 296
  __all__: (none)
```

```
FILE: level_5/data_structure/tabular/sparse_tabular_dataset.py
  Classes:
    - SparseTabularDataset
        Methods: __init__(self, X: Union[np.ndarray, np.memmap, Path, str], y: Union[spmatrix, np.ndarray], indices: Optional[np.ndarray]=None, label_smoothing: float=0.0)
                 __len__(self) -> int
                 __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Union, Optional, Tuple [stdlib]
    - from scipy.sparse import csr_matrix, issparse, spmatrix [third_party]
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 270
  __all__: (none)
```

```
FILE: level_5/datasets/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .load_and_validate_test_data import load_and_validate_test_data [relative]
    - from .prepare_test_dataframe import prepare_test_dataframe_with_dummy_targets [relative]
    - from .splits import get_dataset_cache_dir, save_dataset_splits, load_dataset_splits, apply_train_val_split [relative]
    - from .variants import get_max_augmentation_variant, get_dataset_variant_grid [relative]
  Line count: 22
  __all__: load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets, get_dataset_cache_dir, save_dataset_splits, load_dataset_splits, apply_train_val_split, get_max_augmentation_variant, get_dataset_variant_grid
```

```
FILE: level_5/datasets/load_and_validate_test_data.py
  Classes: (none)
  Functions:
    - load_and_validate_test_data(test_csv_path: Union[str, Path], image_path_column: str='image_path') -> pd.DataFrame
  Imports:
    - import pandas [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
    - from layers.layer_0_core.level_4 import load_csv [internal]
  Line count: 92
  __all__: (none)
```

```
FILE: level_5/datasets/prepare_test_dataframe.py
  Classes: (none)
  Functions:
    - prepare_test_dataframe_with_dummy_targets(unique_df: pd.DataFrame, image_path_column: str, target_cols: List[str]) -> pd.DataFrame
  Imports:
    - import pandas [third_party]
    - from typing import List [stdlib]
  Line count: 30
  __all__: (none)
```

```
FILE: level_5/datasets/splits.py
  Classes: (none)
  Functions:
    - get_dataset_cache_dir() -> Path
    - save_dataset_splits(train_df: pd.DataFrame, val_df: pd.DataFrame, cache_key: str, metadata: Optional[Dict[str, Any]]=None) -> Path
    - load_dataset_splits(cache_key: str) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]
    - apply_train_val_split(data: Any, validation_split: float, random_state: int=42) -> Tuple[Any, Any]
  Imports:
    - import pandas [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, is_kaggle [internal]
    - from layers.layer_0_core.level_2 import get_train_test_split [internal]
    - from layers.layer_0_core.level_4 import save_json [internal]
  Line count: 229
  __all__: (none)
```

```
FILE: level_5/datasets/variants.py
  Classes: (none)
  Functions:
    - _get_preprocessing_and_augmentation_options() -> Tuple[List[str], List[str]]
    - get_max_augmentation_variant() -> Tuple[List[str], List[str]]
    - get_dataset_variant_grid() -> List[Tuple[List[str], List[str]]]
  Imports:
    - from typing import List, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, generate_power_set, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION [internal]
  Line count: 75
  __all__: (none)
```

```
FILE: level_5/ensembling/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .combine import apply_weighted_combination, combine_with_fallback [relative]
    - from .stacking_ensemble import StackingEnsemble [relative]
  Line count: 10
  __all__: ["apply_weighted_combination", "combine_with_fallback", "StackingEnsemble"]
```

```
FILE: level_5/ensembling/combine.py
  Classes: (none)
  Functions:
    - apply_weighted_combination(stacked: np.ndarray, normalized_weights: np.ndarray) -> np.ndarray
    - combine_with_fallback(stacked: np.ndarray, weights_array: np.ndarray, predictions_list: List[np.ndarray], ensemble_name: str) -> np.ndarray
  Imports:
    - import numpy [third_party]
    - from typing import List [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import ensure_positive_weights, normalize_weights [internal]
    - from layers.layer_0_core.level_2 import simple_average [internal]
  Line count: 119
  __all__: (none)
```

```
FILE: level_5/ensembling/stacking_ensemble.py
  Classes:
    - StackingEnsemble
        Methods: __init__(self, model_paths: List[str], model_configs: List[Dict[str, Any]], feature_extraction_model_name: str, n_folds: int=5, meta_model_alpha: float=10.0, random_state: int=42)
                 _load_models(self) -> None
                 _infer_model_name(self, idx: int, model_path: str) -> str
                 generate_oof_predictions(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]
                 fit_meta_models(self, oof_preds: Dict[str, np.ndarray], y_train: np.ndarray) -> None
                 predict(self, test_preds: Dict[str, np.ndarray]) -> np.ndarray
                 _to_2d(arr: np.ndarray) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import get_ridge, get_kfold [internal]
    - from layers.layer_0_core.level_3 import create_regression_model [internal]
    - from layers.layer_0_core.level_4 import load_pickle [internal]
  Line count: 439
  __all__: (none)
```

```
FILE: level_5/export/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .export_pipeline import ExportPipeline [relative]
    - from .operations import find_trained_model_path, export_from_training_dir, copy_model_checkpoint, write_metadata_file [relative]
  Line count: 17
  __all__: ExportPipeline, find_trained_model_path, export_from_training_dir, copy_model_checkpoint, write_metadata_file
```

```
FILE: level_5/export/export_pipeline.py
  Classes:
    - ExportPipeline
        Methods: __init__(self, config: Any, model_path: str, export_dir: Optional[str]=None, model_type: str='vision', **kwargs)
                 setup(self) -> None
                 execute(self) -> Dict[str, Any]
                 _extract_config_metadata(self) -> Dict[str, Any]
                 cleanup(self) -> None
  Functions: (none)
  Imports:
    - from typing import Dict, Any, Optional [stdlib]
    - from pathlib import Path [stdlib]
    - import shutil [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger [internal]
    - from layers.layer_0_core.level_1 import BasePipeline, validate_config_section_exists [internal]
    - from layers.layer_0_core.level_4 import save_json [internal]
  Line count: 286
  __all__: (none)
```

```
FILE: level_5/export/operations.py
  Classes: (none)
  Functions:
    - find_trained_model_path(model_dir: Path, best_fold: int=None) -> tuple[Path, int]
    - _find_model_for_specific_fold(model_dir: Path, fold: int) -> tuple[Path, int]
    - _find_best_fold_model(model_dir: Path) -> tuple[Path, int]
    - _check_regular_checkpoint(fold_dir: Path) -> tuple[Optional[Path], float]
    - _check_regression_model(fold_dir: Path) -> tuple[Optional[Path], float]
    - _extract_score_from_json(path: Path, default: float=-float('inf')) -> float
    - _extract_score_from_checkpoint_metadata(fold_dir: Path) -> float
    - _extract_score_from_regression_info(info_path: Path) -> float
    - export_from_training_dir(model_dir: Path, export_dir: Path, metadata: Dict[str, Any]) -> None
    - copy_model_checkpoint(source: Path, dest: Path) -> None
    - write_metadata_file(metadata: Dict[str, Any], dest: Path) -> None
  Imports:
    - import shutil [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Dict, Any, Optional [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger [internal]
    - from layers.layer_0_core.level_4 import save_json, load_json [internal]
  Line count: 436
  __all__: (none)
```

```
FILE: level_5/file_io/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .merge import merge_json_from_input_and_working, merge_list_by_key_add_only, merge_list_by_key_working_replaces [relative]
    - from .submission import save_submission_csv [relative]
  Line count: 15
  __all__: merge_json_from_input_and_working, merge_list_by_key_add_only, merge_list_by_key_working_replaces, save_submission_csv
```

```
FILE: level_5/file_io/merge.py
  Classes: (none)
  Functions:
    - merge_list_by_key_add_only(input_items: List[Any], working_items: List[Any], key_fn: Callable[[Any], Any]) -> List[Any]
    - merge_list_by_key_working_replaces(input_items: List[Any], working_items: List[Any], key_fn: Callable[[Any], Any]) -> List[Any]
    - merge_json_from_input_and_working(input_path: Optional[Path], working_path: Path, merge_fn: Callable[[List[Any], List[Any]], List[Any]], expected_type: type=list, file_type: str='JSON') -> List[Any]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Callable, List, Optional [stdlib]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 95
  __all__: (none)
```

```
FILE: level_5/file_io/submission.py
  Classes: (none)
  Functions:
    - save_submission_csv(submission_df: pd.DataFrame, output_path: Optional[str]=None) -> str
  Imports:
    - import pandas [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, is_kaggle [internal]
    - from layers.layer_0_core.level_1 import get_default_submission_csv_path [internal]
    - from layers.layer_0_core.level_4 import save_csv [internal]
  Line count: 34
  __all__: (none)
```

```
FILE: level_5/grid_search/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .checkpoint_cleanup import cleanup_checkpoints, cleanup_grid_search_checkpoints_retroactive [relative]
    - from .result_analysis import analyze_results_for_focused_grid, extract_parameter_ranges, extract_top_results, get_focused_parameter_grid, load_raw_results [relative]
    - from .results_persistence import load_checkpoint, load_results, save_checkpoint, save_results [relative]
    - from .variant_tracking import get_next_variant_index, load_completed_variants_helper, save_variant_result_helper [relative]
  Line count: 38
  __all__: see source (load_results, save_results, load_checkpoint, save_checkpoint, load_raw_results, extract_top_results, extract_parameter_ranges, analyze_results_for_focused_grid, get_focused_parameter_grid, cleanup_grid_search_checkpoints_retroactive, cleanup_checkpoints, load_completed_variants_helper, get_next_variant_index, save_variant_result_helper)
```

```
FILE: level_5/grid_search/checkpoint_cleanup.py
  Classes: (none)
  Functions:
    - _delete_non_top_dirs(candidate_dirs: List[Path], keep_names: Set[str]) -> Tuple[int, int]
    - cleanup_grid_search_checkpoints_retroactive(model_base_dir: str, results_file: str, keep_top_n: int=20) -> Tuple[int, int]
    - cleanup_checkpoints(grid_search_dir: Path, keep_top_n: int=5, results: Optional[List[Dict[str, Any]]]=None) -> None
  Imports:
    - import shutil [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Optional, Set, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import extract_results_list, get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 153
  __all__: (none)
```

```
FILE: level_5/grid_search/result_analysis.py
  Classes: (none)
  Functions:
    - load_raw_results(results_file: Union[str, Path]) -> List[Dict[str, Any]]
    - extract_top_results(results: List[Dict[str, Any]], top_n: int=10, metric_key: str='cv_score') -> List[Dict[str, Any]]
    - extract_parameter_ranges(top_results: List[Dict[str, Any]], range_expansion_factor: float=1.5, min_values_per_param: int=2) -> Dict[str, List[Any]]
    - analyze_results_for_focused_grid(results_file: str, top_n: int=10, range_expansion_factor: float=1.5, min_values_per_param: int=2, metric_key: str='cv_score') -> Dict[str, List[Any]]
    - get_focused_parameter_grid(base_search_type: str, previous_results_file: str, top_n_results: int=10, range_expansion_factor: float=1.5, min_values_per_param: int=2) -> Dict[str, List[Any]]
    - _extract_numeric_range(param_values: List[Any], range_expansion_factor: float, min_values_per_param: int, param_name: str) -> List[float]
    - _extract_categorical_values(param_values: List[Any], min_values_per_param: int, param_name: str) -> List[Any]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Union [stdlib]
    - from layers.layer_0_core.level_0 import extract_results_list, get_logger, merge_focused_ranges_into_base_grid [internal]
    - from layers.layer_0_core.level_1 import get_transformer_hyperparameter_grid [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 304
  __all__: (none)
```

```
FILE: level_5/grid_search/results_persistence.py
  Classes: (none)
  Functions:
    - load_results(results_file: Path) -> Tuple[List[Dict], float, Any, Set]
    - save_results(results_file: Path, grid_search_type: str, total_variants: int, completed_count: int, best_score: float, best_variant: Any, results: List[Dict[str, Any]]) -> None
    - load_checkpoint(checkpoint_dir: Optional[Path], param_grid: Optional[Dict]=None) -> Optional[Tuple[List[Dict], float, Any, Set]]
    - save_checkpoint(checkpoint_dir: Optional[Path], grid_search_type: str, param_grid: Dict, results: List[Dict], best_variant: Any, best_score: float, completed_variants: Set, total_variants: int, quick_mode: bool) -> None
    - _extract_checkpoint_timestamp(filepath: Path) -> str
  Imports:
    - from pathlib import Path [stdlib]
    - from datetime import datetime [stdlib]
    - from typing import Any, Dict, List, Optional, Set, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import extract_results_list, get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json, save_json [internal]
  Line count: 379
  __all__: (none)
```

```
FILE: level_5/grid_search/variant_tracking.py
  Classes: (none)
  Functions:
    - load_completed_variants_helper(results_file: Optional[Path], keep_top_n: int, create_variant_key_from_result_fn: Callable[[Dict[str, Any]], Optional[Any]]) -> Tuple[Set[Any], Set[Any], List[Dict[str, Any]], int]
    - get_next_variant_index(all_results: List[Dict[str, Any]]) -> int
    - save_variant_result_helper(result: Dict[str, Any], results_file: Path) -> None
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Callable, Dict, List, Optional, Set, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import extract_results_list, get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json, save_json [internal]
  Line count: 124
  __all__: (none)
```

```
FILE: level_5/metadata/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .paths import find_project_input_root, find_metadata_dir, get_writable_metadata_dir, load_combo_metadata [relative]
    - from .scores import extract_scores_from_json, resolve_best_fold_and_score [relative]
  Line count: 17
  __all__: find_project_input_root, find_metadata_dir, get_writable_metadata_dir, load_combo_metadata, extract_scores_from_json, resolve_best_fold_and_score
```

```
FILE: level_5/metadata/paths.py
  Classes: (none)
  Functions:
    - _find_project_input_root(from_file: str) -> Optional[Path]
    - find_project_input_root(from_file: str) -> Optional[Path]
    - _find_project_working_root(from_file: str) -> Optional[Path]
    - find_metadata_dir(dataset_name: str, from_file: Optional[str]=None) -> Optional[Path]
    - get_writable_metadata_dir(dataset_name: str, from_file: Optional[str]=None) -> Path
    - load_combo_metadata(metadata_dir: Path, subpath: str) -> dict
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Optional [stdlib]
    - from layers.layer_0_core.level_0 import is_kaggle, ensure_dir [internal]
    - from layers.layer_0_core.level_4 import load_json [internal]
  Line count: 130
  __all__: find_project_input_root, find_metadata_dir, get_writable_metadata_dir, load_combo_metadata
```

```
FILE: level_5/metadata/scores.py
  Classes: (none)
  Functions:
    - extract_scores_from_json(*, model_path: Path, json_filename: str, best_fold: Optional[int]) -> tuple[float, list, Optional[int]]
    - resolve_best_fold_and_score(*, best_fold: Optional[int], extracted_best_fold: Optional[int], fold_scores: list, cv_score: float) -> tuple[Optional[int], float]
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_4 import load_json_raw [internal]
  Line count: 48
  __all__: (none)
```

```
FILE: level_5/model_io/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .model_io import load_model, load_model_raw, save_model, save_model_raw [relative]
    - from .model_saver_helper import save_regression_model [relative]
  Line count: 12
  __all__: save_model_raw, save_model, load_model_raw, load_model, save_regression_model
```

```
FILE: level_5/model_io/model_io.py
  Classes: (none)
  Functions:
    - save_model_raw(model: Any, path: Union[str, Path], metadata: Optional[Dict[str, Any]]=None) -> Path
    - save_model(model: Any, path: Union[str, Path], metadata: Optional[Dict[str, Any]]=None) -> Path
    - load_model_raw(path: Union[str, Path]) -> Tuple[Any, Optional[Dict[str, Any]]]
    - load_model(path: Union[str, Path]) -> Tuple[Any, Optional[Dict[str, Any]]]
    - _save_pytorch_model(model: Any, path: Path, metadata: Optional[Dict[str, Any]]) -> None
    - _save_pickle_backed_model(model: Any, path: Path, metadata: Optional[Dict[str, Any]]) -> None
    - _load_pytorch_model(path: Path) -> Tuple[Any, Optional[Dict[str, Any]]]
    - _load_pickle_model(path: Path) -> Tuple[Any, Optional[Dict[str, Any]]]
    - _save_metadata(path: Path, metadata: Dict[str, Any]) -> None
    - _load_metadata(path: Path) -> Optional[Dict[str, Any]]
    - _get_model_type_name(model: Any) -> str
  Imports:
    - from datetime import datetime [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import ModelError, ModelLoadError, ensure_dir, get_logger, get_torch, is_torch_available [internal]
    - from layers.layer_0_core.level_3 import validate_file_exists [internal]
    - from layers.layer_0_core.level_4 import load_json, load_pickle, save_json, save_pickle [internal]
  Line count: 533
  __all__: (none)
```

```
FILE: level_5/model_io/model_saver_helper.py
  Classes: (none)
  Functions:
    - save_regression_model(model: Any, save_dir: Path) -> None
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir [internal]
    - from layers.layer_0_core.level_4 import save_pickle, save_json [internal]
  Line count: 56
  __all__: (none)
```

```
FILE: level_5/training/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .base_model_trainer import BaseModelTrainer [relative]
    - from .vision_trainer import VisionTrainer [relative]
  Line count: 9
  __all__: ["BaseModelTrainer", "VisionTrainer"]
```

```
FILE: level_5/training/base_model_trainer.py
  Classes:
    - BaseModelTrainer
        Methods: __init__(self, config: Union[Any, Dict[str, Any]], device: Optional[Any]=None, model: Optional[Any]=None, model_name: Optional[str]=None, num_primary_targets: Optional[int]=None, image_size: Optional[Tuple[int, int]]=None, dataset_type: str='split', metric_calculator: Optional[Any]=None)
                 _build_model(self, model: Optional[Any]) -> Any
                 _apply_multi_gpu(self, model: Any) -> Any
                 _build_criterion_optimizer_scheduler(self) -> Tuple[Any, Any, Any]
                 _build_phase_helpers(self, metric_calculator: Optional[Any]) -> Tuple[Any, Any, Any]
                 train_epoch(self, train_loader: DataLoader) -> float
                 validate(self, val_loader: DataLoader) -> Tuple[float, float, Any]
                 _run_epoch(self, epoch: int, num_epochs: int, train_loader: DataLoader, val_loader: DataLoader) -> Tuple[float, float, float]
                 _save_if_best(self, epoch: int, metric: float, save_dir: Optional[Path]) -> bool
                 train(self, train_loader: DataLoader, val_loader: DataLoader, num_epochs: Optional[int]=None, save_dir: Optional[Union[str, Path]]=None, resume: bool=True, early_stopping_patience: Optional[int]=None) -> List[Dict]
  Functions: (none)
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Dict, List, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch [internal]
    - from layers.layer_0_core.level_1 import get_device, setup_mixed_precision [internal]
    - from layers.layer_0_core.level_2 import extract_config_settings, get_training_config_value, create_optimizer, create_scheduler, create_loss_function, finalize_epoch, ModelCheckpointer, TrainingPhaseExecutor, ValidationPhaseExecutor [internal]
    - from layers.layer_0_core.level_4 import create_vision_model [internal]
  Line count: 557
  __all__: (none)
```

```
FILE: level_5/training/vision_trainer.py
  Classes:
    - VisionTrainer
        Methods: __init__(self, model: nn.Module, criterion: nn.Module, optimizer: torch.optim.Optimizer, device: torch.device, scheduler: Optional[torch.optim.lr_scheduler._LRScheduler]=None, use_mixed_precision: bool=False)
                 _make_batch_processor(self)
                 train_epoch(self, train_loader: DataLoader, epoch: int) -> float
                 validate(self, val_loader: DataLoader, epoch: int) -> Tuple[float, Optional[float]]
                 fit(self, train_loader: DataLoader, val_loader: DataLoader, num_epochs: int, early_stopping_patience: Optional[int]=None, checkpoint_dir: Optional[str]=None, verbose: bool=True) -> Dict
                 save_checkpoint(self, path) -> None
                 load_checkpoint(self, path: str) -> None
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Dict, List, Optional, Tuple [stdlib]
    - from tqdm import tqdm [third_party]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch, extract_batch_data [internal]
    - from layers.layer_0_core.level_1 import train_one_epoch, load_model_checkpoint, forward_with_amp [internal]
    - from layers.layer_0_core.level_4 import calculate_metrics [internal]
  Line count: 221
  __all__: (none)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_5/__init__.py
  Exports: combined __all__ from batch_loading, data_structure, datasets, ensembling, export, file_io, grid_search, metadata, model_io, training
  Re-exports from: those subpackages (star-import aggregation)
```

```
INIT: level_5/batch_loading/__init__.py — Exports: load_csv_batch, load_image_batch
INIT: level_5/data_structure/__init__.py — Exports: base.__all__ + tabular.__all__
INIT: level_5/data_structure/base/__init__.py — Exports: JSONConfigLoader, create_json_model_registry
INIT: level_5/data_structure/tabular/__init__.py — Exports: BaseTabularModel, SparseTabularDataset
INIT: level_5/datasets/__init__.py — Exports: per §2 datasets/__init__.py __all__
INIT: level_5/ensembling/__init__.py — Exports: apply_weighted_combination, combine_with_fallback, StackingEnsemble
INIT: level_5/export/__init__.py — Exports: ExportPipeline, find_trained_model_path, export_from_training_dir, copy_model_checkpoint, write_metadata_file
INIT: level_5/file_io/__init__.py — Exports: merge_json_from_input_and_working, merge_list_by_key_add_only, merge_list_by_key_working_replaces, save_submission_csv
INIT: level_5/grid_search/__init__.py — Exports: per §2 grid_search/__init__.py __all__
INIT: level_5/metadata/__init__.py — Exports: find_project_input_root, find_metadata_dir, get_writable_metadata_dir, load_combo_metadata, extract_scores_from_json, resolve_best_fold_and_score
INIT: level_5/model_io/__init__.py — Exports: save_model_raw, save_model, load_model_raw, load_model, save_regression_model
INIT: level_5/training/__init__.py — Exports: BaseModelTrainer, VisionTrainer
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  Logic and barrels predominantly use `from layers.layer_0_core.level_K import ...` with K ∈ {0,1,2,3,4} and no imports from level_5 in non-init logic modules observed.
  From level_4: load_csv, load_image, load_json, load_json_raw, save_csv, save_json, save_pickle, load_pickle, create_vision_model, calculate_metrics
  From level_3: validate_path_is_file, validate_file_exists, create_regression_model
  From level_2: get_train_test_split, simple_average, get_ridge, get_kfold, plus training/helper symbols as listed in §2
  From level_1: load_batch, BasePipeline, validate_config_section_exists, get_transformer_hyperparameter_grid, train_one_epoch, load_model_checkpoint, forward_with_amp, get_device, setup_mixed_precision, ensure_positive_weights, normalize_weights, get_default_submission_csv_path
  From level_0: get_logger, ensure_dir, is_kaggle, extract_results_list, merge_focused_ranges_into_base_grid, generate_power_set, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION, ModelError, ModelLoadError, get_torch, is_torch_available, extract_batch_data, ensure_file_dir
  Same-level (level_5) in logic files: none (`from layers.layer_0_core.level_5` not observed outside potential future barrels)
  From level_6+: none observed
  Relative imports: __init__ modules for submodule aggregation only
```

---

#### 5. Flags

```
FLAGS:
  level_5/grid_search/result_analysis.py — 304 lines (>300)
  level_5/ensembling/stacking_ensemble.py — 439 lines (>300)
  level_5/export/operations.py — 436 lines (>300)
  level_5/grid_search/results_persistence.py — 379 lines (>300)
  level_5/model_io/model_io.py — 533 lines (>300); text contains "compat"
  level_5/training/base_model_trainer.py — 557 lines (>300)
  level_5/data_structure/tabular/base.py — 296 lines (approaching split threshold)
  level_5/data_structure/tabular/sparse_tabular_dataset.py — 270 lines
  level_5/datasets/prepare_test_dataframe.py — 30 lines (small utility)
```

---

#### 6. Static scan summary (optional)

- Precheck artifact reports **precheck_status: skipped_machine_script** (**ModuleNotFoundError: No module named 'torchvision'**); no machine violation list merged.

**Machine-generated (verify):** none (`inventory_bootstrap_path` not provided).

</think>


<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>
Read