---
generated: 2026-04-08
audit_scope: general
level_name: level_4
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
---

# INVENTORY: level_4

#### 1. Package & File Tree

```
level_4/
  README.md
  __init__.py
  dataloaders/
    __init__.py
    README.md
    create_dataloaders.py
  ensemble/
    __init__.py
    README.md
    meta_model_stacking.py
  features/
    __init__.py
    README.md
    compute_siglip_embeddings.py
    siglip_adapter.py
  file_io/
    __init__.py
    README.md
    csv.py
    images.py
    json.py
    memmap.py
    pickle.py
    yaml.py
  metrics/
    __init__.py
    README.md
    calculate_metrics.py
    weighted_r2.py
  models/
    __init__.py
    README.md
    vision_model_factory.py
  pipeline/
    __init__.py
    README.md
    evaluate_pipeline.py
    submission_averaging.py
    threshold_optimization.py
  runtime/
    __init__.py
    README.md
    progress_tracker.py
```

---

#### 2. Per-File Details

```
FILE: level_4/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import dataloaders [relative]
    - from . import ensemble [relative]
    - from . import features [relative]
    - from . import file_io [relative]
    - from . import metrics [relative]
    - from . import models [relative]
    - from . import pipeline [relative]
    - from . import runtime [relative]
    - from .dataloaders import * [relative]
    - from .ensemble import * [relative]
    - from .features import * [relative]
    - from .file_io import * [relative]
    - from .metrics import * [relative]
    - from .models import * [relative]
    - from .pipeline import * [relative]
    - from .runtime import * [relative]
  Line count: 30
  __all__: tuple composition of subpackage __all__ lists (dataloaders, ensemble, features, file_io, metrics, models, pipeline, runtime)
```

```
FILE: level_4/dataloaders/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .create_dataloaders import create_dataloaders, create_test_dataloader [relative]
  Line count: 14
  __all__: ["create_dataloaders", "create_test_dataloader"]
```

```
FILE: level_4/dataloaders/create_dataloaders.py
  Classes: (none)
  Functions:
    - create_dataloaders(train_data: pd.DataFrame, val_data: pd.DataFrame, image_dir: str, image_col: str='image_id', target_cols: Optional[list]=None, image_size: int=224, batch_size: int=32, num_workers: int=4, pin_memory: bool=True, augmentation: str='medium', train_transform: Optional[Callable]=None, val_transform: Optional[Callable]=None, seed: int=42) -> Tuple[Any, Any]
    - create_test_dataloader(test_data: pd.DataFrame, image_dir: str, image_col: str='image_id', image_size: int=224, batch_size: int=32, num_workers: int=4, pin_memory: bool=True, test_transform: Optional[Callable]=None) -> Any
  Imports:
    - import pandas [third_party]
    - from typing import Tuple, Optional, Callable, Any [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import build_preprocessing_transforms, create_dataloader_from_dataset, create_dataset_for_test_dataloader, create_datasets_for_dataloaders, create_worker_init_fn, validate_dataframe [internal]
    - from layers.layer_0_core.level_3 import build_transforms_for_dataloaders [internal]
  Line count: 320
  __all__: (none)
```

```
FILE: level_4/ensemble/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .meta_model_stacking import stacking_ensemble_with_validation [relative]
  Line count: 7
  __all__: ["stacking_ensemble_with_validation"]
```

```
FILE: level_4/ensemble/meta_model_stacking.py
  Classes: (none)
  Functions:
    - _validate_meta_model_type(meta_model_type: str) -> None
    - stacking_ensemble_with_validation(base_predictions_train: List[np.ndarray], base_predictions_val: List[np.ndarray], y_val: np.ndarray, meta_model_type: str='ridge', meta_model_params: Optional[Dict[str, Any]]=None, random_state: int=42) -> np.ndarray
  Imports:
    - import numpy [third_party]
    - from typing import Any, Dict, List, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, DataValidationError, validate_targets [internal]
    - from layers.layer_0_core.level_1 import validate_paired_predictions [internal]
    - from layers.layer_0_core.level_3 import create_meta_model [internal]
  Line count: 233
  __all__: (none)
```

```
FILE: level_4/features/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .compute_siglip_embeddings import compute_siglip_embeddings [relative]
    - from .siglip_adapter import SigLIPFeatureExtractorAdapter [relative]
  Line count: 9
  __all__: ["compute_siglip_embeddings", "SigLIPFeatureExtractorAdapter"]
```

```
FILE: level_4/features/compute_siglip_embeddings.py
  Classes: (none)
  Functions:
    - compute_siglip_embeddings(model_path: str, df: pd.DataFrame, image_path_col: str='image_path', image_root: Optional[Union[str, Path]]=None, **kwargs) -> np.ndarray
  Imports:
    - import numpy [third_party]
    - import pandas [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Optional, Union [stdlib]
    - from layers.layer_0_core.level_3 import SigLIPExtractor [internal]
  Line count: 42
  __all__: (none)
```

```
FILE: level_4/features/siglip_adapter.py
  Classes:
    - SigLIPFeatureExtractorAdapter
        Methods: __init__(self, siglip_extractor: SigLIPExtractor)
                 get_input_size(self) -> Tuple[int, int]
                 extract_features(self, x: torch.Tensor) -> torch.Tensor
  Functions: (none)
  Imports:
    - from typing import Tuple [stdlib]
    - import numpy [third_party]
    - from PIL import Image [third_party]
    - from layers.layer_0_core.level_0 import get_torch [internal]
    - from layers.layer_0_core.level_3 import SigLIPExtractor [internal]
  Line count: 100
  __all__: (none)
```

```
FILE: level_4/file_io/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .csv import load_csv_raw, load_csv_raw_if_exists, load_csv, save_csv [relative]
    - from .images import load_image_raw, load_image, save_image [relative]
    - from .json import load_json_raw, load_json, load_best_config_json, save_json, save_json_atomic [relative]
    - from .memmap import should_use_memmap, create_memmap, load_memmap, save_memmap_with_metadata, load_memmap_with_metadata, MEMMAP_THRESHOLD_MB [relative]
    - from .pickle import PICKLE_HIGHEST_PROTOCOL, load_pickle_raw, load_pickle, save_pickle [relative]
    - from .yaml import load_yaml_raw, load_yaml, save_yaml [relative]
  Line count: 63
  __all__: load_csv_raw, load_csv_raw_if_exists, load_csv, save_csv, load_image_raw, load_image, save_image, load_json_raw, load_json, load_best_config_json, save_json, save_json_atomic, should_use_memmap, create_memmap, load_memmap, save_memmap_with_metadata, load_memmap_with_metadata, MEMMAP_THRESHOLD_MB, PICKLE_HIGHEST_PROTOCOL, load_pickle_raw, load_pickle, save_pickle, load_yaml_raw, load_yaml, save_yaml
```

```
FILE: level_4/file_io/csv.py
  Classes: (none)
  Functions:
    - load_csv_raw(path: Union[str, Path], **kwargs) -> pd.DataFrame
    - load_csv_raw_if_exists(path: Union[str, Path], **kwargs) -> Optional[pd.DataFrame]
    - load_csv(path: Union[str, Path], *, required_cols: Optional[List[str]]=None, min_rows: int=1, **kwargs) -> pd.DataFrame
    - save_csv(df: pd.DataFrame, path: Union[str, Path], *, index: bool=False, **kwargs) -> None
  Imports:
    - import pandas [third_party]
    - from pathlib import Path [stdlib]
    - from typing import List, Optional, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataValidationError, ensure_dir [internal]
    - from layers.layer_0_core.level_2 import validate_dataframe [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
  Line count: 118
  __all__: (none)
```

```
FILE: level_4/file_io/images.py
  Classes: (none)
  Functions:
    - load_image_raw(path: Union[str, Path]) -> Image.Image
    - load_image(path: Union[str, Path], *, convert_rgb: bool=True) -> Image.Image
    - save_image(image: Image.Image, path: Union[str, Path], format: Optional[str]=None, **kwargs) -> None
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Union, Optional [stdlib]
    - from PIL import Image [third_party]
    - from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, ensure_dir, load_image_pil [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
  Line count: 191
  __all__: (none)
```

```
FILE: level_4/file_io/json.py
  Classes: (none)
  Functions:
    - load_json_raw(path: Union[str, Path]) -> Any
    - load_json(path: Union[str, Path], *, expected_type: Optional[Type]=None, file_type: str='JSON') -> Any
    - save_json(data: Any, path: Union[str, Path], *, indent: int=2, ensure_ascii: bool=False) -> None
    - save_json_atomic(data: Any, path: Union[str, Path], *, indent: int=2, ensure_ascii: bool=False) -> None
    - load_best_config_json(path: Union[str, Path], *, drop_keys: Optional[Iterable[str]]=None) -> dict[str, Any]
  Imports:
    - import json [stdlib]
    - import os [stdlib]
    - import tempfile [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Any, Iterable, Optional, Type, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, ensure_dir [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
  Line count: 163
  __all__: (none)
```

```
FILE: level_4/file_io/memmap.py
  Classes: (none)
  Functions:
    - should_use_memmap(shape: Tuple[int, ...], dtype: np.dtype=np.float32, threshold_mb: float=MEMMAP_THRESHOLD_MB) -> bool
    - create_memmap(path: Path, shape: Tuple[int, ...], dtype: np.dtype=np.float32, mode: str='w+') -> np.memmap
    - load_memmap(path: Path, mode: str='r') -> np.memmap
    - save_memmap_with_metadata(array: np.ndarray, path: Path, metadata: Optional[Dict[str, Any]]=None, dtype: np.dtype=np.float32) -> Path
    - load_memmap_with_metadata(path: Path, mode: str='r') -> Tuple[np.memmap, Dict[str, Any]]
  Imports:
    - import numpy [third_party]
    - import json [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Tuple, Optional, Dict, Any [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, DataValidationError, ensure_dir [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
  Line count: 240
  __all__: (none)
```

```
FILE: level_4/file_io/pickle.py
  Classes: (none)
  Functions:
    - load_pickle_raw(path: Union[str, Path]) -> Any
    - load_pickle(path: Union[str, Path]) -> Any
    - save_pickle(data: Any, path: Union[str, Path], *, protocol: Optional[int]=None) -> None
  Imports:
    - import pickle [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Any, Optional, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, DataValidationError, ensure_dir [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
  Line count: 89
  __all__: (none)
```

```
FILE: level_4/file_io/yaml.py
  Classes: (none)
  Functions:
    - load_yaml_raw(path: Union[str, Path]) -> Any
    - load_yaml(path: Union[str, Path]) -> Any
    - save_yaml(data: Any, path: Union[str, Path]) -> None
  Imports:
    - import yaml [third_party]
    - from pathlib import Path [stdlib]
    - from typing import Any, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, DataValidationError, ensure_dir [internal]
    - from layers.layer_0_core.level_3 import validate_path_is_file [internal]
  Line count: 159
  __all__: (none)
```

```
FILE: level_4/metrics/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .calculate_metrics import calculate_metrics, calculate_metric_by_name [relative]
    - from .weighted_r2 import create_weighted_r2_calculator [relative]
  Line count: 10
  __all__: ["calculate_metrics", "calculate_metric_by_name", "create_weighted_r2_calculator"]
```

```
FILE: level_4/metrics/calculate_metrics.py
  Classes: (none)
  Functions:
    - calculate_metrics(task_type: str, y_true: np.ndarray, y_pred: np.ndarray, contest: Optional[str]=None, **kwargs) -> Dict[str, float]
    - calculate_metric_by_name(metric_name: str, y_true: np.ndarray, y_pred: np.ndarray, **kwargs) -> Union[float, Dict[str, Any]]
  Imports:
    - import numpy [third_party]
    - from typing import Dict, Optional, Any, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import get_metric, list_metrics [internal]
    - from layers.layer_0_core.level_3 import calculate_classification_metrics, calculate_regression_metrics [internal]
  Line count: 303
  __all__: (none)
```

```
FILE: level_4/metrics/weighted_r2.py
  Classes: (none)
  Functions:
    - create_weighted_r2_calculator(weights: Dict[str, float], target_order: List[str], derived_target_fn: Optional[Callable[[np.ndarray], np.ndarray]]=None) -> Callable[[np.ndarray, np.ndarray, Optional[Any]], Tuple[float, np.ndarray]]
  Imports:
    - import numpy [third_party]
    - from typing import Any, Callable, Dict, List, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_2 import validate_paired_arrays [internal]
    - from layers.layer_0_core.level_3 import calculate_r2_per_target, prepare_weighted_arrays, calculate_weighted_r2_from_arrays [internal]
  Line count: 53
  __all__: (none)
```

```
FILE: level_4/models/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .vision_model_factory import create_vision_model [relative]
  Line count: 13
  __all__: ["create_vision_model"]
```

```
FILE: level_4/models/vision_model_factory.py
  Classes: (none)
  Functions:
    - create_vision_model(model_name: str, num_classes: int, pretrained: bool=True, input_size: Optional[Tuple[int, int]]=None, **kwargs) -> BaseVisionModel
  Imports:
    - from typing import Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import BaseVisionModel [internal]
    - from layers.layer_0_core.level_2 import DINOv2Model [internal]
    - from layers.layer_0_core.level_3 import TimmModel [internal]
  Line count: 161
  __all__: (none)
```

```
FILE: level_4/pipeline/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .evaluate_pipeline import EvaluatePipeline [relative]
    - from .submission_averaging import SubmissionAveragingWorkflow [relative]
    - from .threshold_optimization import optimize_threshold [relative]
  Line count: 11
  __all__: ["EvaluatePipeline", "SubmissionAveragingWorkflow", "optimize_threshold"]
```

```
FILE: level_4/pipeline/evaluate_pipeline.py
  Classes:
    - EvaluatePipeline
        Methods: __init__(self, config: Any, predictions: Optional[np.ndarray]=None, ground_truth: Optional[np.ndarray]=None, predictions_path: Optional[str]=None, ground_truth_path: Optional[str]=None, model_type: str='vision', **kwargs)
                 setup(self) -> None
                 execute(self) -> Dict[str, Any]
                 _save_metrics(self, output_path: Path) -> None
                 _evaluate_vision(self) -> Dict[str, Any]
                 _evaluate_tabular(self) -> Dict[str, Any]
                 cleanup(self) -> None
  Functions: (none)
  Imports:
    - import numpy [third_party]
    - import json [stdlib]
    - from typing import Dict, Any, Optional [stdlib]
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger [internal]
    - from layers.layer_0_core.level_1 import BasePipeline, validate_config_section_exists [internal]
    - from layers.layer_0_core.level_3 import calculate_regression_metrics, calculate_f1, calculate_precision, calculate_recall, calculate_roc_auc [internal]
  Line count: 358
  __all__: (none)
```

```
FILE: level_4/pipeline/submission_averaging.py
  Classes:
    - SubmissionAveragingWorkflow
        Methods: __init__(self, config: Any, submission_files: List[str], ensemble_method: str='average', weights: Optional[List[float]]=None, output_path: Optional[str]=None, **kwargs)
                 setup(self) -> None
                 execute(self) -> Dict[str, Any]
                 _load_submission_file(self, filepath: str) -> Dict[tuple, float]
                 _convert_predictions_to_arrays(self, predictions_list: List[Dict[tuple, float]]) -> tuple[List[np.ndarray], List[tuple]]
                 _apply_ensemble_to_arrays(self, pred_arrays: List[np.ndarray]) -> np.ndarray
                 _apply_weighted_average(self, pred_arrays: List[np.ndarray]) -> np.ndarray
                 _apply_power_average(self, pred_arrays: List[np.ndarray]) -> np.ndarray
                 _apply_percentile_average(self, pred_arrays: List[np.ndarray]) -> np.ndarray
                 _apply_ensemble_method(self, predictions_list: List[Dict[tuple, float]]) -> Dict[tuple, float]
                 _save_submission(self, predictions: Dict[tuple, float], output_path: str) -> None
                 cleanup(self) -> None
  Functions: (none)
  Imports:
    - import time [stdlib]
    - import numpy [third_party]
    - import shutil [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import List, Optional, Dict, Any [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, validate_submission_format [internal]
    - from layers.layer_0_core.level_1 import BasePipeline [internal]
    - from layers.layer_0_core.level_2 import simple_average, weighted_average, value_rank_average, value_percentile_average, power_average, geometric_mean, max_ensemble [internal]
  Line count: 574
  __all__: (none)
```

```
FILE: level_4/pipeline/threshold_optimization.py
  Classes: (none)
  Functions:
    - optimize_threshold(y_true: np.ndarray, y_pred_proba: np.ndarray, metric: str='f1', threshold_range: Tuple[float, float]=(0.0, 1.0)) -> float
  Imports:
    - import numpy [third_party]
    - from scipy.optimize import minimize_scalar [third_party]
    - from typing import Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_3 import calculate_f1, calculate_precision, calculate_recall [internal]
  Line count: 118
  __all__: (none)
```

```
FILE: level_4/runtime/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .progress_tracker import ProgressTracker [relative]
  Line count: 7
  __all__: ["ProgressTracker"]
```

```
FILE: level_4/runtime/progress_tracker.py
  Classes:
    - ProgressTracker
        Methods: __init__(self, config: ProgressConfig)
                 _get_device_memory_info() -> Dict[str, str]
                 create_bar(self, bar_id: str, total: int, desc: str, level: int=1, unit: str='it', initial: int=0, **kwargs) -> Optional[str]
                 update(self, bar_id: str, n: int=1, **metrics_kwargs: Any) -> None
                 set_postfix(self, bar_id: str, **metrics_kwargs: Any) -> None
                 close(self, bar_id: str) -> None
                 close_all(self) -> None
                 get_elapsed_time(self, bar_id: str) -> Optional[float]
  Functions: (none)
  Imports:
    - from typing import Optional, Any, Dict [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_1 import ProgressConfig, get_device_info [internal]
    - from layers.layer_0_core.level_2 import ProgressMetrics, ProgressBarManager [internal]
    - from layers.layer_0_core.level_3 import ProgressFormatter [internal]
  Line count: 273
  __all__: (none)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_4/__init__.py
  Exports: union of subpackage __all__ (create_dataloaders, create_test_dataloader, stacking_ensemble_with_validation, compute_siglip_embeddings, SigLIPFeatureExtractorAdapter, file_io symbols, calculate_metrics, calculate_metric_by_name, create_weighted_r2_calculator, create_vision_model, EvaluatePipeline, SubmissionAveragingWorkflow, optimize_threshold, ProgressTracker)
  Re-exports from: level_4.dataloaders, level_4.ensemble, level_4.features, level_4.file_io, level_4.metrics, level_4.models, level_4.pipeline, level_4.runtime
```

```
INIT: level_4/dataloaders/__init__.py
  Exports: create_dataloaders, create_test_dataloader
  Re-exports from: level_4.dataloaders.create_dataloaders
```

```
INIT: level_4/ensemble/__init__.py
  Exports: stacking_ensemble_with_validation
  Re-exports from: level_4.ensemble.meta_model_stacking
```

```
INIT: level_4/features/__init__.py
  Exports: compute_siglip_embeddings, SigLIPFeatureExtractorAdapter
  Re-exports from: level_4.features.compute_siglip_embeddings, level_4.features.siglip_adapter
```

```
INIT: level_4/file_io/__init__.py
  Exports: see §2 file_io/__init__.py __all__ list
  Re-exports from: level_4.file_io.csv, images, json, memmap, pickle, yaml
```

```
INIT: level_4/metrics/__init__.py
  Exports: calculate_metrics, calculate_metric_by_name, create_weighted_r2_calculator
  Re-exports from: level_4.metrics.calculate_metrics, level_4.metrics.weighted_r2
```

```
INIT: level_4/models/__init__.py
  Exports: create_vision_model
  Re-exports from: level_4.models.vision_model_factory
```

```
INIT: level_4/pipeline/__init__.py
  Exports: EvaluatePipeline, SubmissionAveragingWorkflow, optimize_threshold
  Re-exports from: level_4.pipeline.evaluate_pipeline, submission_averaging, threshold_optimization
```

```
INIT: level_4/runtime/__init__.py
  Exports: ProgressTracker
  Re-exports from: level_4.runtime.progress_tracker
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From level_0 .. level_3 (N=4): all logic modules use `from layers.layer_0_core.level_K import ...` with K ∈ {0,1,2,3} only — consistent with lower-tier dependencies.
  From level_0 (representative): get_logger, ensure_dir, DataLoadError, DataValidationError, DataProcessingError, get_torch, validate_submission_format, validate_targets, load_image_pil, ensure_dir
  From level_1: BasePipeline, BaseVisionModel, validate_config_section_exists, validate_paired_predictions, ProgressConfig, get_device_info, get_metric, list_metrics
  From level_2: build_preprocessing_transforms, create_dataloader_from_dataset, create_dataset_for_test_dataloader, create_datasets_for_dataloaders, create_worker_init_fn, validate_dataframe, DINOv2Model, simple_average, weighted_average, value_rank_average, value_percentile_average, power_average, geometric_mean, max_ensemble, validate_paired_arrays, ProgressMetrics, ProgressBarManager
  From level_3: build_transforms_for_dataloaders, SigLIPExtractor, TimmModel, create_meta_model, validate_path_is_file, calculate_classification_metrics, calculate_regression_metrics, calculate_r2_per_target, prepare_weighted_arrays, calculate_weighted_r2_from_arrays, calculate_f1, calculate_precision, calculate_recall, calculate_roc_auc, ProgressFormatter
  From same level (level_4) in logic files: none (no `from layers.layer_0_core.level_4` in non-barrel modules observed)
  From level_5 or higher: none observed
  In __init__.py and package barrels: relative imports (`from .` / `from .pkg import *`) — aggregation only
```

---

#### 5. Flags

```
FLAGS:
  level_4/dataloaders/create_dataloaders.py — 320 lines (>300)
  level_4/metrics/calculate_metrics.py — 303 lines (>300)
  level_4/pipeline/evaluate_pipeline.py — 358 lines (>300)
  level_4/pipeline/submission_averaging.py — 574 lines (>300)
  level_4/features/siglip_adapter.py — text contains "compat" (keyword match)
  level_4/pipeline/threshold_optimization.py — uses scipy (third_party)
```

---

#### 6. Static scan summary (optional)

- Precheck artifact reports **precheck_status: skipped_machine_script** (environment could not import devtools stack: **ModuleNotFoundError: No module named 'torchvision'**).
- No machine violation list merged; inventory is from source tree only.

**Machine-generated (verify):** none (`inventory_bootstrap_path` not provided).
