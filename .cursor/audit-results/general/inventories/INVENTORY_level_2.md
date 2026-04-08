---
generated: 2026-04-08
audit_scope: general
level_name: level_2
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
---

# INVENTORY: `level_2`

## 1. Package & File Tree

```
level_2/
  README.md
  __init__.py
  analysis/
    README.md
    __init__.py
    cv_analysis.py
  dataloader/
    README.md
    __init__.py
    datasets.py
    loader.py
    streaming_datasets.py
    workers.py
  ensemble_strategies/
    README.md
    __init__.py
    averaging.py
    result_handler_common.py
    weight_matrix_builder.py
  feature_extractors/
    README.md
    __init__.py
    cache_io.py
    feature_extractor.py
    protein_feature_extractor.py
    semantic_features.py
  grid_search/
    README.md
    __init__.py
    environment_setup.py
    param_grid.py
    variant_accumulator.py
  inference/
    README.md
    __init__.py
    vision_predictor.py
  models/
    README.md
    __init__.py
    dinov2_model.py
    regression_base.py
    sklearn_imports.py
    timm_loader.py
  progress/
    README.md
    __init__.py
    bar_manager.py
    metrics_calculator.py
  runtime/
    README.md
    __init__.py
    environment.py
  training/
    README.md
    __init__.py
    checkpointer.py
    component_factories.py
    config_helper.py
    epoch_finalization.py
    epoch_runners.py
    multitask_config.py
    training_executor.py
    validation_executor.py
    memory/
      README.md
      __init__.py
      oom_recovery.py
      resource_cleanup.py
  validation/
    README.md
    __init__.py
    arrays.py
    dataframes.py
    lists.py
    series.py
  vision_transforms/
    README.md
    __init__.py
    build_transforms.py
    image_cleaning.py
    preprocessing_registry.py
    tta.py
    augmentation/
      README.md
      __init__.py
      presets.py
      registry.py
```

---

## 2. Per-File Details

### FILE: `level_2/__init__.py`

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from . import analysis` [internal]
- `from . import dataloader` [internal]
- `from . import ensemble_strategies` [internal]
- `from . import feature_extractors` [internal]
- `from . import grid_search` [internal]
- `from . import inference` [internal]
- `from . import models` [internal]
- `from . import progress` [internal]
- `from . import runtime` [internal]
- `from . import training` [internal]
- `from . import validation` [internal]
- `from . import vision_transforms` [internal]
- `from .analysis import *` [internal]
- `from .dataloader import *` [internal]
- `from .ensemble_strategies import *` [internal]
- `from .feature_extractors import *` [internal]
- `from .grid_search import *` [internal]
- `from .inference import *` [internal]
- `from .models import *` [internal]
- `from .progress import *` [internal]
- `from .runtime import *` [internal]
- `from .training import *` [internal]
- `from .validation import *` [internal]
- `from .vision_transforms import *` [internal]

**Line count:** 42

**__all__:** tuple expression concatenating subpackage `__all__` lists (see §3)

---

### FILE: `level_2/analysis/__init__.py`

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .cv_analysis import find_best_fold_from_scores, analyze_cv_test_gap, analyze_fold_score_range` [internal]

**Line count:** 9

**__all__:** `['find_best_fold_from_scores', 'analyze_cv_test_gap', 'analyze_fold_score_range']`

---

### FILE: `level_2/analysis/cv_analysis.py`

**Module docstring:** Fold score analysis utilities for cross-validation results.

**Classes:** (none)

**Functions:**

- `find_best_fold_from_scores(fold_scores: List[float]) -> Tuple[int, float]`
- `analyze_cv_test_gap(cv_score: float, fold_scores: List[float], test_score: Optional[float] = None, threshold: float = 0.15) -> Dict[str, Any]`
- `analyze_fold_score_range(fold_scores: List[float], threshold: float = 0.2) -> Dict[str, Any]`

**Imports:**

- `import math` [stdlib]
- `from typing import List, Tuple, Dict, Any, Optional` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import calculate_fold_statistics, generate_cv_test_gap_warnings` [internal — level_1]

**Line count:** 146

**__all__:** (not present)

---

### FILE: `level_2/dataloader/__init__.py`

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .datasets import create_dataset_for_test_dataloader, create_datasets_for_dataloaders` [internal]
- `from .loader import create_dataloader_from_dataset` [internal]
- `from .streaming_datasets import create_streaming_dataset_for_test` [internal]
- `from .workers import create_worker_init_fn` [internal]

**Line count:** 14

**__all__:** `['create_datasets_for_dataloaders', 'create_dataset_for_test_dataloader', 'create_dataloader_from_dataset', 'create_streaming_dataset_for_test', 'create_worker_init_fn']`

---

### FILE: `level_2/dataloader/datasets.py`

**Module docstring:** Dataset construction helpers for training and validation dataloaders.

**Classes:** (none)

**Functions:**

- `create_dataset_for_test_dataloader(data: pd.DataFrame, image_dir: str, image_col: str, transform: Callable) -> BaseImageDataset`
- `create_datasets_for_dataloaders(train_data: pd.DataFrame, val_data: pd.DataFrame, image_dir: str, image_col: str, target_cols: Optional[List[str]], train_transform: Callable, val_transform: Callable) -> Tuple[BaseImageDataset, BaseImageDataset]`

**Imports:**

- `import pandas as pd` [third-party]
- `from typing import Callable, List, Optional, Tuple` [stdlib]
- `from layers.layer_0_core.level_1 import BaseImageDataset` [internal — level_1]

**Line count:** 78

**__all__:** (not present)

---

### FILE: `level_2/dataloader/loader.py`

**Module docstring:** DataLoader construction from Dataset.

**Classes:** (none)

**Functions:**

- `create_dataloader_from_dataset(dataset: Any, batch_size: int, shuffle: bool = False, num_workers: int = 4, pin_memory: bool = True, worker_init_fn: Optional[Callable] = None, persistent_workers: Optional[bool] = None) -> Any`

**Imports:**

- `from typing import Any, Callable, Optional` [stdlib]
- `from layers.layer_0_core.level_0 import get_torch` [internal — level_0]

**Line count:** 48

**__all__:** (not present)

---

### FILE: `level_2/dataloader/streaming_datasets.py`

**Module docstring:** Streaming dataset factory for test inference.

**Classes:** (none)

**Functions:**

- `create_streaming_dataset_for_test(data: pd.DataFrame, data_root: str, transform: Callable, target_cols: List[str], dataset_type: str, image_path_column: str = 'image_path') -> Union[StreamingDataset, StreamingSplitDataset]`

**Imports:**

- `import pandas as pd` [third-party]
- `from typing import Callable, List, Union` [stdlib]
- `from layers.layer_0_core.level_1 import StreamingDataset, StreamingSplitDataset` [internal — level_1]

**Line count:** 46

**__all__:** (not present)

---

### FILE: `level_2/dataloader/workers.py`

**Module docstring:** Worker initialisation for deterministic DataLoader behaviour.

**Classes:** (none)

**Functions:**

- `create_worker_init_fn(seed: int) -> Callable[[int], None]`

**Imports:**

- `from typing import Callable` [stdlib]
- `from layers.layer_0_core.level_1 import set_seed` [internal — level_1]

**Line count:** 24

**__all__:** (not present)

---

### FILE: `level_2/ensemble_strategies/__init__.py`

**Module docstring:** Ensemble strategy implementations (combining predictions).

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .averaging import (model_rank_weights, simple_average, weighted_average, value_rank_average, value_percentile_average, power_average, geometric_mean, max_ensemble, merge_submissions)` [internal]
- `from .result_handler_common import _log_pipeline_completion` [internal]
- `from .weight_matrix_builder import build_weight_matrix` [internal]

**Line count:** 39

**__all__:** `['model_rank_weights', 'simple_average', 'weighted_average', 'value_rank_average', 'value_percentile_average', 'power_average', 'geometric_mean', 'max_ensemble', 'merge_submissions', '_log_pipeline_completion', 'build_weight_matrix']`

---

### FILE: `level_2/ensemble_strategies/averaging.py`

**Module docstring:** Averaging ensemble functions (pure functional API).

**Classes:** (none)

**Functions:**

- `model_rank_weights(scores: np.ndarray) -> np.ndarray`
- `simple_average(predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray`
- `weighted_average(predictions_list: List[np.ndarray], weights: List[float]) -> np.ndarray`
- `value_rank_average(predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray`
- `value_percentile_average(predictions_list: List[np.ndarray], percentile: float = 50.0) -> np.ndarray`
- `power_average(predictions_list: List[np.ndarray], power: float = 1.5, weights: Optional[List[float]] = None) -> np.ndarray`
- `geometric_mean(predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray`
- `max_ensemble(predictions_list: List[np.ndarray]) -> np.ndarray`
- `merge_submissions(predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray`

**Imports:**

- `import numpy as np` [third-party]
- `from typing import List, Optional` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, DataValidationError` [internal — level_0]
- `from layers.layer_0_core.level_1 import validate_predictions_for_ensemble, normalize_weights` [internal — level_1]

**Line count:** 233

**__all__:** (not present)

---

### FILE: `level_2/ensemble_strategies/result_handler_common.py`

**Module docstring:** Shared logic for pipeline result handlers.

**Classes:** (none)

**Functions:**

- `_log_pipeline_completion(returncode: int, stdout_lines: List[str], log_file: str, operation_name: str, log_items: List[Tuple[str, Any]], success_header: Optional[str] = None, success_footer: Optional[List[str]] = None) -> None`

**Imports:**

- `from typing import Any, List, Optional, Tuple` [stdlib]
- `from layers.layer_0_core.level_0 import ExecutionResult, get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import validate_execution_result` [internal — level_1]

**Line count:** 36

**__all__:** (not present)

---

### FILE: `level_2/ensemble_strategies/weight_matrix_builder.py`

**Module docstring:** Weight matrix builder for ensemble strategies.

**Classes:** (none)

**Functions:**

- `build_weight_matrix(per_target_weights: Dict[str, List[float]], target_names: List[str], num_models: int) -> np.ndarray`

**Imports:**

- `import numpy as np` [third-party]
- `from typing import Dict, List` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import ensure_positive_weights` [internal — level_1]

**Line count:** 68

**__all__:** (not present)

---

### FILE: `level_2/feature_extractors/__init__.py`

**Module docstring:** Feature extractors (re-exports).

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .cache_io import (get_feature_cache_paths, find_feature_cache, save_features, load_features, resolve_extraction_info)` [internal]
- `from .feature_extractor import FeatureExtractor` [internal]
- `from .protein_feature_extractor import extract_handcrafted_features` [internal]
- `from .semantic_features import SemanticFeatureExtractor, generate_semantic_features` [internal]

**Line count:** 24

**__all__:** `['get_feature_cache_paths', 'find_feature_cache', 'save_features', 'load_features', 'resolve_extraction_info', 'FeatureExtractor', 'extract_handcrafted_features', 'SemanticFeatureExtractor', 'generate_semantic_features']`

---

### FILE: `level_2/feature_extractors/cache_io.py`

**Module docstring:** Feature cache IO: save, load, locate, and resolve extraction info from disk.

**Classes:** (none)

**Functions:**

- `get_feature_cache_paths(filename: str) -> Tuple[Path, Path]`
- `find_feature_cache(filename: str) -> Optional[Path]`
- `save_features(all_features: np.ndarray, all_targets: np.ndarray, fold_assignments: np.ndarray, filename: str, model_name: str, dataset_type: str = 'split', image_size: Optional[Tuple[int, int]] = None, preprocessing_list: Optional[list] = None, use_input_dir: bool = True) -> Path`
- `load_features(cache_path: Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]`
- `resolve_extraction_info(feature_filename: str) -> Dict[str, Any]`
- `_build_metadata(filename: str, model_name: str, dataset_type: str, image_size: Optional[Tuple[int, int]], preprocessing_list: Optional[list], all_features: np.ndarray, all_targets: np.ndarray, fold_assignments: np.ndarray) -> Dict[str, Any]`
- `_write_npz(save_path: Path, all_features: np.ndarray, all_targets: np.ndarray, fold_assignments: np.ndarray, metadata: Dict[str, Any]) -> None`

**Imports:**

- `import json` [stdlib]
- `import numpy as np` [third-party]
- `from pathlib import Path` [stdlib]
- `from typing import Any, Dict, Optional, Tuple` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import (get_cache_base_paths, get_model_name_from_model_id, get_metadata_dir, parse_feature_filename)` [internal — level_1]

**Line count:** 248

**__all__:** (not present)

---

### FILE: `level_2/feature_extractors/feature_extractor.py`

**Module docstring:** Extract features from model backbone; no TTA.

**Classes:**

- **FeatureExtractor** (`BaseFeatureExtractor`)
  - **Methods:**
    - `__init__(self, model: torch.nn.Module, device: torch.device)`
    - `extract_features(self, dataloader: DataLoader, dataset_type: str = 'split') -> np.ndarray`
    - `extract_features_and_targets(self, dataloader: DataLoader, dataset_type: str = 'split') -> Tuple[np.ndarray, np.ndarray]`
    - `_extract_features_single_pass(self, dataloader: DataLoader, dataset_type: str) -> np.ndarray`
    - `_extract_from_model(self, x: torch.Tensor) -> torch.Tensor`

**Functions:** (none)

**Imports:**

- `from typing import Tuple` [stdlib]
- `import numpy as np` [third-party]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import BaseFeatureExtractor` [internal — level_1]

**Line count:** 105

**__all__:** (not present)

---

### FILE: `level_2/feature_extractors/protein_feature_extractor.py`

**Module docstring:** Handcrafted features for protein sequences.

**Classes:** (none)

**Functions:**

- `_hydrophobic_fraction(region: str) -> float`
- `_charged_fraction(region: str) -> float`
- `extract_handcrafted_features(seq: str) -> np.ndarray`

**Imports:**

- `import numpy as np` [third-party]
- `from collections import Counter` [stdlib]
- `from layers.layer_0_core.level_0 import (AA_ALPHABET, TOP_DIPEPTIDES, TOP_TRIPEPTIDES, HANDCRAFTED_FEATURE_DIM, extract_kmer_frequencies)` [internal — level_0]
- `from layers.layer_0_core.level_1 import (calculate_physicochemical_properties, calculate_ctd_features)` [internal — level_1]

**Line count:** 127

**__all__:** (not present)

---

### FILE: `level_2/feature_extractors/semantic_features.py`

**Module docstring:** Semantic feature extraction via text probing.

**Classes:**

- **SemanticFeatureExtractor** (`BaseFeatureExtractor`)
  - **Methods:**
    - `__init__(self, model_path: str, concept_groups: Dict[str, List[str]], device: Optional[torch.device] = None)`
    - `_encode_concepts(self) -> Dict[str, torch.Tensor]`
    - `extract_semantic_scores(self, image_embeddings: Union[np.ndarray, torch.Tensor]) -> np.ndarray`
    - `extract_features(self, image_embeddings: Union[np.ndarray, torch.Tensor], **kwargs: Any) -> np.ndarray`
    - `__call__(self, image_embeddings: Union[np.ndarray, torch.Tensor], **kwargs: Any) -> np.ndarray`

**Functions:**

- `generate_semantic_features(image_embeddings: np.ndarray, model_path: str, concept_groups: Dict[str, List[str]], device: Optional[torch.device] = None) -> np.ndarray`

**Imports:**

- `import numpy as np` [third-party]
- `from typing import Any, Dict, List, Optional, Union` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import BaseFeatureExtractor, get_siglip_text_classes` [internal — level_1]

**Line count:** 151

**__all__:** (not present)

---

### FILE: `level_2/grid_search/__init__.py`

**Module docstring:** Grid search utilities.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .environment_setup import (apply_memory_optimizations, create_grid_search_dir, normalize_base_model_dir, setup_grid_search_environment)` [internal]
- `from .param_grid import resolve_keyed_param_grid` [internal]
- `from .variant_accumulator import accumulate_variant_results` [internal]

**Line count:** 19

**__all__:** `['setup_grid_search_environment', 'apply_memory_optimizations', 'normalize_base_model_dir', 'create_grid_search_dir', 'resolve_keyed_param_grid', 'accumulate_variant_results']`

---

### FILE: `level_2/grid_search/environment_setup.py`

**Module docstring:** Environment and directory setup utilities for grid search.

**Classes:** (none)

**Functions:**

- `setup_grid_search_environment(config: Union[Any, Dict[str, Any]], grid_search_type_fn) -> Tuple[Any, Path, Path, Any]`
- `apply_memory_optimizations(config: Union[Any, Dict[str, Any]]) -> None`
- `normalize_base_model_dir(config: Union[Any, Dict[str, Any]], grid_search_type: str, paths: Any) -> Path`
- `create_grid_search_dir(config: Union[Any, Dict[str, Any]], grid_search_type: str, paths: Any) -> Path`

**Imports:**

- `from pathlib import Path` [stdlib]
- `from typing import Tuple, Any, Union, Dict` [stdlib]
- `from layers.layer_0_core.level_0 import ensure_dir, ConfigValidationError, get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import get_device, get_device_info` [internal — level_1]

**Line count:** 127

**__all__:** (not present)

---

### FILE: `level_2/grid_search/param_grid.py`

**Module docstring:** Keyed parameter grid resolution.

**Classes:** (none)

**Functions:**

- `resolve_keyed_param_grid(grid_config: Dict[str, Any], key: Optional[str] = None, quick_mode: bool = False, keyed_grids_field: str = 'param_grids') -> Dict[str, List]`

**Imports:**

- `from typing import Any, Dict, List, Optional` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import resolve_param_grid` [internal — level_1]

**Line count:** 51

**__all__:** (not present)

---

### FILE: `level_2/grid_search/variant_accumulator.py`

**Module docstring:** Variant result accumulation for grid search runs.

**Classes:** (none)

**Functions:**

- `accumulate_variant_results(variants: List[Any], run_variant_fn: Callable, create_key_fn: Callable, accumulated_results: Optional[List[Dict[str, Any]]] = None, accumulated_completed: Optional[Set] = None, save_results_fn: Callable = lambda: None, save_checkpoint_fn: Callable = lambda: None, score_key: str = 'score') -> Dict[str, Any]`

**Imports:**

- `from typing import Callable, Dict, List, Any, Set, Optional` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import execute_variants` [internal — level_1]

**Line count:** 57

**__all__:** (not present)

---

### FILE: `level_2/inference/__init__.py`

**Module docstring:** Inference package for model inference.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .vision_predictor import VisionPredictor` [internal]

**Line count:** 7

**__all__:** `['VisionPredictor']`

---

### FILE: `level_2/inference/vision_predictor.py`

**Module docstring:** Vision model predictor for inference.

**Classes:**

- **VisionPredictor**
  - **Methods:**
    - `__init__(self, model: nn.Module, device: torch.device, use_mixed_precision: bool = False)`
    - `predict(self, dataloader: DataLoader, verbose: bool = True) -> np.ndarray`
    - `predict_single(self, image: torch.Tensor) -> np.ndarray`

**Functions:** (none)

**Imports:**

- `import numpy as np` [third-party]
- `from tqdm import tqdm` [third-party]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import forward_with_amp` [internal — level_1]

**Line count:** 82

**__all__:** (not present)

---

### FILE: `level_2/models/__init__.py`

**Module docstring:** Model wrappers and lazy-loaded sklearn/boosting components.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .dinov2_model import DINOv2Model` [internal]
- `from .regression_base import BaseMultiOutputRegressionModel` [internal]
- `from .sklearn_imports import (get_catboost, get_cross_val_score, get_elastic_net, get_gaussian_mixture, get_gradient_boosting_regressor, get_hist_gradient_boosting_regressor, get_kfold, get_lasso, get_lgbm_classifier, get_lightgbm, get_linear_regression, get_logistic_regression, get_pca, get_pls_regression, get_random_forest_regressor, get_ridge, get_ridge_classifier, get_standard_scaler, get_stratified_kfold, get_train_test_split, get_xgb_classifier, get_xgboost)` [internal]
- `from .timm_loader import TimmWeightLoader` [internal]

**Line count:** 57

**__all__:** `['DINOv2Model', 'BaseMultiOutputRegressionModel', 'get_standard_scaler', 'get_pca', 'get_pls_regression', 'get_gaussian_mixture', 'get_gradient_boosting_regressor', 'get_hist_gradient_boosting_regressor', 'get_random_forest_regressor', 'get_catboost', 'get_lightgbm', 'get_lgbm_classifier', 'get_xgboost', 'get_xgb_classifier', 'get_ridge', 'get_logistic_regression', 'get_ridge_classifier', 'get_linear_regression', 'get_lasso', 'get_elastic_net', 'get_kfold', 'get_stratified_kfold', 'get_train_test_split', 'get_cross_val_score', 'TimmWeightLoader']`

---

### FILE: `level_2/models/dinov2_model.py`

**Module docstring:** DINOv2 model wrapper for vision tasks.

**Classes:**

- **DINOv2Model** (`BaseVisionModel`)
  - **Methods:**
    - `__init__(self, model_name: str = 'facebook/dinov2-base', pretrained: bool = True, num_classes: int = 1, input_size: Optional[Tuple[int, int]] = None, use_tiles: bool = False, tile_grid_size: int = 2, use_film: bool = False)`
    - `_load_hf_model_with_retry(self, model_name: str) -> HFDinov2Model`
    - `_load_backbone(self, model_name: str, pretrained: bool) -> None`
    - `_init_heads(self) -> None`
    - `_init_fusion_module(self) -> None`
    - `_extract_hf_features(self, x: torch.Tensor) -> torch.Tensor`
    - `_extract_tiles(self, img: torch.Tensor) -> torch.Tensor`
    - `_process_tiles(self, img: torch.Tensor) -> torch.Tensor`
    - `forward(self, x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]) -> torch.Tensor`
    - `get_input_size(self) -> Tuple[int, int]`
    - `freeze_backbone(self) -> None`
    - `unfreeze_backbone(self) -> None`
    - `is_pretrained(self) -> bool`

**Functions:** (none)

**Imports:**

- `import warnings` [stdlib]
- `from typing import Tuple, Optional, Union` [stdlib]
- `from transformers import Dinov2Model as HFDinov2Model` [third-party]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import FiLM, BaseVisionModel` [internal — level_1]

**Line count:** 314

**__all__:** (not present)

---

### FILE: `level_2/models/regression_base.py`

**Module docstring:** Tabular/sklearn regression models for multi-output regression.

**Classes:**

- **BaseMultiOutputRegressionModel**
  - **Methods:**
    - `__init__(self, **params)`
    - `fit(self, X: np.ndarray, y: np.ndarray) -> 'BaseMultiOutputRegressionModel'`
    - `predict(self, X: np.ndarray) -> np.ndarray`
    - `_postprocess_predictions(self, predictions: np.ndarray) -> np.ndarray`
    - `get_model(self) -> MultiOutputRegressor`
    - `_get_model_class(self)`
    - `_get_default_params(self) -> dict`
    - `_get_model_name(self) -> str`

**Functions:** (none)

**Imports:**

- `import numpy as np` [third-party]
- `from sklearn.multioutput import MultiOutputRegressor` [third-party]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import check_array_finite` [internal — level_1]

**Line count:** 75

**__all__:** (not present)

---

### FILE: `level_2/models/sklearn_imports.py`

**Module docstring:** Lazy imports for sklearn and boosting components.

**Classes:** (none)

**Functions:**

- `_make_loader(module: str, cls: str, package: str, warn: str) -> Callable[[], Any]`
- `__getattr__(name: str) -> Any`

**Imports:**

- `from typing import Any, Callable, Dict, Tuple` [stdlib]
- `from layers.layer_0_core.level_1 import lazy_import` [internal — level_1]

**Line count:** 50

**__all__:** (not present)

---

### FILE: `level_2/models/timm_loader.py`

**Module docstring:** timm model loading with pretrained weight fallback strategies.

**Classes:**

- **TimmWeightLoader**
  - **Methods:**
    - `__init__(self) -> None`
    - `is_pretrained_loaded(self) -> bool`
    - `_try_pretrained(self, model_name: str, num_classes: int) -> Optional[object]`
    - `_try_offline_cache(self, model_name: str, num_classes: int, original_error: Exception) -> Optional[object]`
    - `load_weights(self, model_name: str, num_classes: int, pretrained: bool = True) -> object`

**Functions:**

- `_create_timm_model(model_name: str, num_classes: int, pretrained: bool) -> object`
- `_is_network_error(error: Exception) -> bool`

**Imports:**

- `import timm` [third-party]
- `from typing import Optional` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import (configure_huggingface_cache, resolve_offline_weight_cache)` [internal — level_1]

**Line count:** 140

**__all__:** (not present)

---

### FILE: `level_2/progress/__init__.py`

**Module docstring:** Progress display config and bar management.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .bar_manager import ProgressBarManager` [internal]
- `from .metrics_calculator import ProgressMetrics` [internal]

**Line count:** 9

**__all__:** `['ProgressBarManager', 'ProgressMetrics']`

---

### FILE: `level_2/progress/bar_manager.py`

**Module docstring:** Manages tqdm progress bars, positions, and metadata.

**Classes:**

- **ProgressBarManager**
  - **Methods:**
    - `__init__(self, verbosity: Union[int, ProgressVerbosity] = ProgressVerbosity.MODERATE)`
    - `should_show(self, level: int = 1) -> bool`
    - `get_position(self, level: int) -> int`
    - `create_bar(self, bar_id: str, total: int, desc: str, level: int = 1, unit: str = 'it', initial: int = 0, leave: Optional[bool] = None, disable: Optional[bool] = None, **kwargs: Any) -> Optional[str]`
    - `get_bar(self, bar_id: str) -> Optional[tqdm]`
    - `get_metadata(self, bar_id: str) -> Dict[str, Any]`
    - `close(self, bar_id: str) -> None`
    - `close_all(self) -> None`

**Functions:** (none)

**Imports:**

- `from tqdm import tqdm` [third-party]
- `from typing import Dict, Optional, Any, Union` [stdlib]
- `from layers.layer_0_core.level_1 import ProgressVerbosity` [internal — level_1]

**Line count:** 116

**__all__:** (not present)

---

### FILE: `level_2/progress/metrics_calculator.py`

**Module docstring:** Calculates ETA, throughput, and elapsed time for progress bars.

**Classes:**

- **ProgressMetrics**
  - **Methods:**
    - `__init__(self, config: ProgressConfig, memory_info_provider: Optional[Callable[[], Dict[str, str]]] = None)`
    - `register_bar(self, bar_id: str) -> None`
    - `cleanup(self, bar_id: str) -> None`
    - `record_update(self, bar_id: str, n: int) -> None`
    - `estimate_eta(self, bar_id: str, current: int, total: Optional[int]) -> Optional[float]`
    - `calculate_throughput(self, bar_id: str, current: int) -> Optional[float]`
    - `get_memory_info(self) -> Dict[str, str]`
    - `get_elapsed_time(self, bar_id: str) -> Optional[float]`

**Functions:** (none)

**Imports:**

- `import time` [stdlib]
- `from typing import Dict, Optional, Callable` [stdlib]
- `from collections import deque` [stdlib]
- `from layers.layer_0_core.level_1 import ProgressConfig` [internal — level_1]

**Line count:** 116

**__all__:** (not present)

---

### FILE: `level_2/runtime/__init__.py`

**Module docstring:** Runtime package for pipeline execution.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .environment import setup_runtime_environment` [internal]

**Line count:** 7

**__all__:** `['setup_runtime_environment']`

---

### FILE: `level_2/runtime/environment.py`

**Module docstring:** Runtime setup logic for pipeline execution.

**Classes:** (none)

**Functions:**

- `setup_runtime_environment() -> Dict[str, Any]`

**Imports:**

- `from typing import Any, Dict` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, is_kaggle` [internal — level_0]
- `from layers.layer_0_core.level_1 import get_device_info` [internal — level_1]

**Line count:** 40

**__all__:** (not present)

---

### FILE: `level_2/training/__init__.py`

**Module docstring:** Training utilities.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from . import memory` [internal]
- `from .memory import *` [internal]
- `from .checkpointer import ModelCheckpointer` [internal]
- `from .component_factories import create_loss_function, create_optimizer, create_scheduler` [internal]
- `from .epoch_finalization import finalize_epoch` [internal]
- `from .epoch_runners import run_train_epoch, run_validate_epoch` [internal]
- `from .config_helper import (ConfigHelper, extract_config_settings, get_required_config_value, get_training_config_value)` [internal]
- `from .multitask_config import MultiTaskTrainingConfig` [internal]
- `from .training_executor import TrainingPhaseExecutor` [internal]
- `from .validation_executor import ValidationPhaseExecutor` [internal]

**Line count:** 38

**__all__:** `list(memory.__all__) + ['ConfigHelper', 'extract_config_settings', 'get_required_config_value', 'get_training_config_value', 'ModelCheckpointer', 'create_optimizer', 'create_scheduler', 'create_loss_function', 'finalize_epoch', 'run_train_epoch', 'run_validate_epoch', 'MultiTaskTrainingConfig', 'TrainingPhaseExecutor', 'ValidationPhaseExecutor']`

---

### FILE: `level_2/training/checkpointer.py`

**Module docstring:** Model checkpointer for BaseModelTrainer.

**Classes:**

- **ModelCheckpointer**
  - **Methods:**
    - `__init__(self, model: nn.Module, optimizer, scheduler, device: torch.device)`
    - `resume_from_checkpoint(self, save_dir: Path, num_epochs: int) -> Dict[str, Any]`
    - `_build_checkpoint_dict(self, epoch: int, best_score: float, history: List[Dict[str, Any]]) -> Dict[str, Any]`
    - `save_best_model(self, epoch: int, best_score: float, history: List[Dict[str, Any]], save_dir: Path) -> None`

**Functions:** (none)

**Imports:**

- `from pathlib import Path` [stdlib]
- `from typing import Dict, Any, List` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import load_model_checkpoint` [internal — level_1]

**Line count:** 121

**__all__:** (not present)

---

### FILE: `level_2/training/component_factories.py`

**Module docstring:** Training component factories: optimizer, scheduler, loss function.

**Classes:** (none)

**Functions:**

- `_get_param_or_config(param: Optional[Any], config: Union[Any, Dict[str, Any]], config_path: str, default: Any) -> Any`
- `create_optimizer(model: nn.Module, config: Union[Any, Dict[str, Any]], learning_rate: Optional[float] = None, weight_decay: Optional[float] = None, optimizer: Optional[str] = None, **kwargs) -> optim.Optimizer`
- `create_scheduler(optimizer: optim.Optimizer, config: Union[Any, Dict[str, Any]], scheduler: Optional[str] = None, num_epochs: Optional[int] = None, scheduler_mode: Optional[str] = None, scheduler_factor: Optional[float] = None, scheduler_patience: Optional[int] = None, **kwargs) -> Optional[optim.lr_scheduler._LRScheduler]`
- `create_loss_function(config: Union[Any, Dict[str, Any]], loss_function: Optional[str] = None, registry: Optional[Dict[str, Type[nn.Module]]] = None, **kwargs) -> nn.Module`

**Imports:**

- `from typing import Any, Dict, Optional, Type, Union` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch, get_config_value` [internal — level_0]
- `from layers.layer_0_core.level_1 import (FocalLoss, WeightedBCELoss, SparseBCEWithLogitsLoss, LabelSmoothingBCEWithLogitsLoss)` [internal — level_1]

**Line count:** 190

**__all__:** (not present)

---

### FILE: `level_2/training/config_helper.py`

**Module docstring:** Generic configuration helper for trainers.

**Classes:**

- **ConfigHelper**
  - **Methods:**
    - `extract_config_settings(config: Union[Any, Dict[str, Any]], num_primary_targets: Optional[int], model_name: Optional[str], image_size: Optional[Tuple[int, int]]) -> tuple[Optional[int], Optional[str], Optional[Tuple[int, int]]]` (staticmethod)
    - `setup_mixed_precision(config: Union[Any, Dict[str, Any]], model_name: Optional[str], device: Any) -> tuple[bool, Optional[Any]]` (staticmethod)

**Functions:**

- `get_required_config_value(config: Union[Any, Dict[str, Any]], key: str, *, error_msg: str) -> Any`
- `extract_config_settings(config: Union[Any, Dict[str, Any]], num_primary_targets: Optional[int], model_name: Optional[str], image_size: Optional[Tuple[int, int]]) -> tuple[Optional[int], Optional[str], Optional[Tuple[int, int]]]`
- `get_training_config_value(config: Union[Any, Dict[str, Any]], key: str, default: Any) -> Any`

**Imports:**

- `from typing import Dict, Optional, Tuple, Union, Any` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_config_value` [internal — level_0]
- `from layers.layer_0_core.level_1 import setup_mixed_precision` [internal — level_1]

**Line count:** 137

**__all__:** (not present)

---

### FILE: `level_2/training/epoch_finalization.py`

**Module docstring:** Epoch-level orchestration helpers.

**Classes:** (none)

**Functions:**

- `finalize_epoch(*, epoch: int, num_epochs: int, train_loss: float, val_loss: float, metric_name: str, metric_value: float, per_target_scores: List[float], config: Any, scheduler: Any, optimizer: Any) -> Dict[str, Any]`

**Imports:**

- `from typing import Any, Dict, List` [stdlib]
- `from layers.layer_0_core.level_0 import step_scheduler, create_history_entry` [internal — level_0]
- `from layers.layer_0_core.level_1 import log_epoch_progress` [internal — level_1]

**Line count:** 57

**__all__:** (not present)

---

### FILE: `level_2/training/epoch_runners.py`

**Module docstring:** Standard supervised PyTorch epoch templates.

**Classes:** (none)

**Functions:**

- `run_train_epoch(model: nn.Module, train_loader: DataLoader, optimizer: torch.optim.Optimizer, criterion: nn.Module, device: torch.device, scaler: Optional[object] = None, use_tqdm: bool = False) -> float`
- `run_validate_epoch(model: nn.Module, val_loader: DataLoader, criterion: nn.Module, device: torch.device, use_tqdm: bool = False) -> float`

**Imports:**

- `from typing import Optional` [stdlib]
- `from tqdm import tqdm` [third-party]
- `from layers.layer_0_core.level_0 import get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import train_one_epoch, run_supervised_batch` [internal — level_1]

**Line count:** 100

**__all__:** (not present)

---

### FILE: `level_2/training/memory/__init__.py`

**Module docstring:** Memory management utilities for training.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .oom_recovery import is_oom_error, recover_from_oom` [internal]
- `from .resource_cleanup import cleanup_model, release_training_resources` [internal]

**Line count:** 11

**__all__:** `['is_oom_error', 'recover_from_oom', 'cleanup_model', 'release_training_resources']`

---

### FILE: `level_2/training/memory/oom_recovery.py`

**Module docstring:** OOM recovery utilities.

**Classes:** (none)

**Functions:**

- `_log_cuda_memory(label: str) -> None`
- `is_oom_error(exception: Exception) -> bool`
- `recover_from_oom(model: Optional[Any] = None, delay_seconds: float = 2.0, cleanup_passes: int = 3) -> None`

**Imports:**

- `import gc` [stdlib]
- `import time` [stdlib]
- `from typing import Optional, Any` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import perform_aggressive_cleanup` [internal — level_1]

**Line count:** 115

**__all__:** (not present)

---

### FILE: `level_2/training/memory/resource_cleanup.py`

**Module docstring:** Memory and resource cleanup utilities.

**Classes:** (none)

**Functions:**

- `_safe_cuda_synchronize(torch) -> None`
- `cleanup_model(model: Any) -> None`
- `release_training_resources(dataframe: Any = None, dataset: Any = None, dataloader: Any = None, model: Any = None, aggressive: bool = True, delay_seconds: float = 0.5) -> None`
- `_cleanup_dataframe(dataframe: Any) -> bool`
- `_cleanup_dataset(dataset: Any) -> None`
- `_cleanup_dataloader(dataloader: Any) -> None`
- `_cleanup_cuda(aggressive: bool, delay_seconds: float) -> None`

**Imports:**

- `import gc` [stdlib]
- `import time` [stdlib]
- `from typing import Any` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import is_cuda_available, perform_aggressive_cleanup` [internal — level_1]

**Line count:** 208

**__all__:** (not present)

---

### FILE: `level_2/training/multitask_config.py`

**Module docstring:** Multi-task / multi-head training configuration extensions.

**Classes:**

- **MultiTaskTrainingConfig** (`TrainingConfig`, dataclass)
  - **Fields:** `per_task_hyperparams: Optional[Dict[str, Dict[str, Any]]] = None`
  - **Methods:**
    - `get_task_params(self, task_id: str) -> Dict[str, Any]`

**Functions:** (none)

**Imports:**

- `from dataclasses import dataclass` [stdlib]
- `from typing import Dict, Any, Optional` [stdlib]
- `from layers.layer_0_core.level_1 import TrainingConfig` [internal — level_1]

**Line count:** 46

**__all__:** (not present)

---

### FILE: `level_2/training/training_executor.py`

**Module docstring:** Training phase executor for BaseModelTrainer.

**Classes:**

- **TrainingPhaseExecutor**
  - **Methods:**
    - `__init__(self, model: nn.Module, device: torch.device, criterion: nn.Module, optimizer: torch.optim.Optimizer, scheduler: Any, use_mixed_precision: bool, scaler: Any)`
    - `process_batch(self, batch: Tuple) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]`
    - `_make_batch_processor(self)`
    - `train_epoch(self, train_loader: DataLoader) -> float`

**Functions:** (none)

**Imports:**

- `from typing import Any, Tuple` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import train_one_epoch, run_supervised_batch` [internal — level_1]

**Line count:** 61

**__all__:** (not present)

---

### FILE: `level_2/training/validation_executor.py`

**Module docstring:** Validation phase executor for BaseModelTrainer.

**Classes:**

- **ValidationPhaseExecutor**
  - **Methods:**
    - `__init__(self, model: nn.Module, device: torch.device, criterion: nn.Module, config: Any, metric_calculator: Callable)`
    - `process_batch(self, batch: Tuple) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]`
    - `validate(self, val_loader: DataLoader) -> Tuple[float, float, np.ndarray]`

**Functions:** (none)

**Imports:**

- `import numpy as np` [third-party]
- `from typing import Any, Callable, List, Tuple` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, get_torch` [internal — level_0]
- `from layers.layer_0_core.level_1 import run_supervised_batch` [internal — level_1]

**Line count:** 90

**__all__:** (not present)

---

### FILE: `level_2/validation/__init__.py`

**Module docstring:** Validation utilities.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .arrays import validate_array, validate_model_output, validate_paired_arrays` [internal]
- `from .dataframes import validate_dataframe, validate_column_values` [internal]
- `from .lists import validate_list, validate_list_not_empty` [internal]
- `from .series import validate_series` [internal]

**Line count:** 17

**__all__:** `['validate_array', 'validate_model_output', 'validate_paired_arrays', 'validate_dataframe', 'validate_column_values', 'validate_list', 'validate_list_not_empty', 'validate_series']`

---

### FILE: `level_2/validation/arrays.py`

**Module docstring:** Array validation.

**Classes:** (none)

**Functions:**

- `validate_array(array: np.ndarray, expected_shape: Optional[Tuple[Optional[int], ...]] = None, check_nan: bool = False, check_inf: bool = False, name: str = 'array') -> None`
- `validate_model_output(predictions: np.ndarray, expected_shape: Optional[Tuple[int, ...]] = None, check_nan: bool = True, check_inf: bool = True) -> None`
- `validate_paired_arrays(y_true: np.ndarray, y_pred: np.ndarray, allow_different_shapes: bool = False, name_true: str = 'y_true', name_pred: str = 'y_pred') -> None`

**Imports:**

- `import numpy as np` [third-party]
- `from typing import Optional, Tuple` [stdlib]
- `from layers.layer_0_core.level_0 import DataValidationError` [internal — level_0]
- `from layers.layer_0_core.level_1 import check_not_none, check_array_finite` [internal — level_1]

**Line count:** 146

**__all__:** (not present)

---

### FILE: `level_2/validation/dataframes.py`

**Module docstring:** DataFrame validation.

**Classes:** (none)

**Functions:**

- `validate_dataframe(df: pd.DataFrame, required_columns: Optional[List[str]] = None, min_rows: int = 1, name: str = 'DataFrame') -> None`
- `validate_column_values(df: pd.DataFrame, column: str, check_null: bool = False, check_empty: bool = False, name: str = 'DataFrame') -> None`

**Imports:**

- `import pandas as pd` [third-party]
- `from typing import Optional, List` [stdlib]
- `from layers.layer_0_core.level_0 import DataValidationError` [internal — level_0]
- `from layers.layer_0_core.level_1 import check_not_none, check_min_collection_length` [internal — level_1]

**Line count:** 100

**__all__:** (not present)

---

### FILE: `level_2/validation/lists.py`

**Module docstring:** List validation.

**Classes:** (none)

**Functions:**

- `validate_list(values: Iterable[Any], allowed: Collection[Any], name: str = 'value') -> None`
- `validate_list_not_empty(values: Collection[Any], name: str = 'list') -> None`

**Imports:**

- `from typing import Iterable, Collection, Any` [stdlib]
- `from layers.layer_0_core.level_0 import DataValidationError` [internal — level_0]
- `from layers.layer_0_core.level_1 import check_not_none` [internal — level_1]

**Line count:** 60

**__all__:** (not present)

---

### FILE: `level_2/validation/series.py`

**Module docstring:** Series validation.

**Classes:** (none)

**Functions:**

- `validate_series(series: pd.Series, min_length: int = 1, check_nan: bool = False, unique: bool = False, name: str = 'series') -> None`

**Imports:**

- `import pandas as pd` [third-party]
- `from layers.layer_0_core.level_0 import DataValidationError` [internal — level_0]
- `from layers.layer_0_core.level_1 import check_not_none, check_min_collection_length` [internal — level_1]

**Line count:** 47

**__all__:** (not present)

---

### FILE: `level_2/vision_transforms/__init__.py`

**Module docstring:** Vision transforms: preprocessing, transforms (TTA, mode), augmentation.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from . import augmentation` [internal]
- `from .augmentation import *` [internal]
- `from .build_transforms import build_preprocessing_transforms, build_simple_transforms` [internal]
- `from .image_cleaning import (ImageCleaningConfig, clean_image_batch, clean_image_with_config)` [internal]
- `from .preprocessing_registry import PREPROCESSING_BUILDERS` [internal]
- `from .tta import (TTAVariant, build_tta_transforms, get_all_tta_variants, get_default_tta_variants)` [internal]

**Line count:** 26

**__all__:** `list(augmentation.__all__) + ['build_preprocessing_transforms', 'build_simple_transforms', 'ImageCleaningConfig', 'clean_image_with_config', 'clean_image_batch', 'PREPROCESSING_BUILDERS', 'TTAVariant', 'build_tta_transforms', 'get_default_tta_variants', 'get_all_tta_variants']` (see source)

---

### FILE: `level_2/vision_transforms/augmentation/__init__.py`

**Module docstring:** Vision augmentation: registry, presets, and preset selector.

**Classes:** (none)

**Functions:** (none)

**Imports:**

- `from .presets import (get_light_augmentation, get_medium_augmentation, get_heavy_augmentation, get_custom_augmentation, AugmentationPreset, PRESET_FUNCS, build_augmentation_transforms)` [internal]
- `from .registry import AUGMENTATION_BUILDERS` [internal]

**Line count:** 23

**__all__:** `['get_light_augmentation', 'get_medium_augmentation', 'get_heavy_augmentation', 'get_custom_augmentation', 'AugmentationPreset', 'PRESET_FUNCS', 'build_augmentation_transforms', 'AUGMENTATION_BUILDERS']`

---

### FILE: `level_2/vision_transforms/augmentation/presets.py`

**Module docstring:** Common augmentation presets and preset selector.

**Classes:** (none)

**Functions:**

- `get_light_augmentation() -> List[Any]`
- `get_medium_augmentation() -> List[Any]`
- `get_heavy_augmentation() -> List[Any]`
- `get_custom_augmentation(horizontal_flip: bool = True, vertical_flip: bool = False, rotation_degrees: float = 0.0, color_jitter: bool = False, blur: bool = False) -> List[Any]`
- `build_augmentation_transforms(preset: AugmentationPreset = 'none', additional_transforms: Optional[List] = None) -> List[Any]`

**Imports:**

- `import torchvision.transforms as transforms` [third-party]
- `from typing import List, Any, Optional, Literal` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import get_geometric_transform, get_color_jitter_transform, get_blur_transform` [internal — level_1]

**Line count:** 132

**Module-level:** `AugmentationPreset = Literal['none', 'light', 'medium', 'heavy']`; `PRESET_FUNCS` dict.

---

### FILE: `level_2/vision_transforms/augmentation/registry.py`

**Module docstring:** Augmentation transform builder registry using level_1 augmentation APIs.

**Classes:** (none)

**Functions:**

- `_get_geometric_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]`
- `_get_color_jitter_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]`
- `_get_blurring_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]`
- `_get_noise_addition_augmentation(config: Any) -> Tuple[Optional[Any], Optional[Any]]`

**Imports:**

- `from typing import Dict, Callable, Optional, Any, Tuple` [stdlib]
- `from layers.layer_0_core.level_1 import (get_geometric_transform, get_color_jitter_transform, get_blur_transform, get_noise_transform)` [internal — level_1]

**Line count:** 40

**Module-level:** `AugmentationBuilder` type alias; `AUGMENTATION_BUILDERS` mapping (`geometric_transformations`, `color_jittering`, `blurring`, `noise_addition`).

---

### FILE: `level_2/vision_transforms/build_transforms.py`

**Module docstring:** Preprocessing and training/validation transform pipeline construction.

**Classes:** (none)

**Functions:**

- `build_preprocessing_transforms(image_size: Union[int, Tuple[int, int]], normalize: bool = True, mean: Tuple[float, float, float] = IMAGENET_MEAN, std: Tuple[float, float, float] = IMAGENET_STD, center_crop: bool = False, additional_transforms: Optional[List] = None) -> transforms.Compose`
- `build_simple_transforms(image_size: Union[int, Tuple[int, int]], normalize: bool = False) -> transforms.Compose`

**Imports:**

- `import torchvision.transforms as transforms` [third-party]
- `from typing import List, Optional, Tuple, Union` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, IMAGENET_MEAN, IMAGENET_STD` [internal — level_0]
- `from layers.layer_0_core.level_1 import get_resize_transform, get_normalize_transform` [internal — level_1]

**Line count:** 64

**__all__:** (not present)

---

### FILE: `level_2/vision_transforms/image_cleaning.py`

**Module docstring:** Composable image cleaning pipelines.

**Classes:**

- **ImageCleaningConfig** (dataclass)
  - **Fields:** `crop_keep_ratio: Optional[float] = None`; `hsv_lower: Optional[Tuple[int, int, int]] = None`; `hsv_upper: Optional[Tuple[int, int, int]] = None`; `kernel_size: int = 3`; `iterations: int = 2`; `inpaint_radius: int = 3`

**Functions:**

- `clean_image_with_config(img: np.ndarray, config: ImageCleaningConfig) -> np.ndarray`
- `clean_image_batch(images: List[np.ndarray], config: ImageCleaningConfig) -> List[np.ndarray]`

**Imports:**

- `import numpy as np` [third-party]
- `from dataclasses import dataclass` [stdlib]
- `from typing import List, Optional, Tuple` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger` [internal — level_0]
- `from layers.layer_0_core.level_1 import crop_relative_height, inpaint_by_hsv_range` [internal — level_1]

**Line count:** 70

**__all__:** (not present)

---

### FILE: `level_2/vision_transforms/preprocessing_registry.py`

**Module docstring:** Preprocessing transform builder registry.

**Classes:** (none)

**Functions:**

- `_get_center_crop_transform(config: Any) -> Optional[transforms.CenterCrop]`
- `_get_resize_from_config(config: Any) -> Optional[Any]`

**Imports:**

- `import torchvision.transforms as transforms` [third-party]
- `from typing import Dict, Callable, Optional, Any` [stdlib]
- `from layers.layer_0_core.level_0 import noise_reduction, get_image_size_from_config` [internal — level_0]
- `from layers.layer_0_core.level_1 import get_resize_transform, contrast_enhancement` [internal — level_1]

**Line count:** 44

**Module-level:** `TransformBuilder` type alias; `PREPROCESSING_BUILDERS` (`resize`, `center_crop`, `contrast_enhancement`, `noise_reduction`).

---

### FILE: `level_2/vision_transforms/tta.py`

**Module docstring:** Test-time augmentation transforms.

**Classes:**

- **TTAVariant** (`Enum`; members: `ORIGINAL`, `H_FLIP`, `V_FLIP`, `HV_FLIP`, `ROTATE_90`, `ROTATE_180`, `ROTATE_270`)

**Functions:**

- `_convert_variants_to_enums(variants: List[Union[TTAVariant, str]]) -> List[TTAVariant]`
- `_build_variant_transform(variant: TTAVariant, base_pil_transforms: List, tensor_transforms: List) -> transforms.Compose`
- `build_tta_transforms(image_size: Union[int, Tuple[int, int]], variants: List[Union[TTAVariant, str]] = None, normalize: bool = True, mean: Tuple[float, float, float] = IMAGENET_MEAN, std: Tuple[float, float, float] = IMAGENET_STD) -> List[transforms.Compose]`
- `get_default_tta_variants() -> List[TTAVariant]`
- `get_all_tta_variants() -> List[TTAVariant]`

**Imports:**

- `import torchvision.transforms as transforms` [third-party]
- `from typing import List, Union, Tuple` [stdlib]
- `from enum import Enum` [stdlib]
- `from layers.layer_0_core.level_0 import get_logger, IMAGENET_MEAN, IMAGENET_STD` [internal — level_0]
- `from layers.layer_0_core.level_1 import get_resize_transform, get_normalize_transform, compose_transform_pipeline` [internal — level_1]

**Line count:** 110

**__all__:** (not present)

---

## 3. `__init__.py` Public API Summary

- **INIT:** `level_2/__init__.py` — **Exports:** union of subpackage `__all__` lists. **Re-exports from:** `analysis`, `dataloader`, `ensemble_strategies`, `feature_extractors`, `grid_search`, `inference`, `models`, `progress`, `runtime`, `training`, `validation`, `vision_transforms`.

- **INIT:** `level_2/analysis/__init__.py` — **Exports:** `find_best_fold_from_scores`, `analyze_cv_test_gap`, `analyze_fold_score_range` — **from:** `cv_analysis`.

- **INIT:** `level_2/dataloader/__init__.py` — **Exports:** dataset/dataloader factories — **from:** `datasets`, `loader`, `streaming_datasets`, `workers`.

- **INIT:** `level_2/ensemble_strategies/__init__.py` — **Exports:** averaging API, `_log_pipeline_completion`, `build_weight_matrix` — **from:** `averaging`, `result_handler_common`, `weight_matrix_builder`.

- **INIT:** `level_2/feature_extractors/__init__.py` — **Exports:** cache IO, `FeatureExtractor`, `extract_handcrafted_features`, `SemanticFeatureExtractor`, `generate_semantic_features` — **from:** submodules as listed in §2.

- **INIT:** `level_2/grid_search/__init__.py` — **Exports:** `setup_grid_search_environment`, `apply_memory_optimizations`, `normalize_base_model_dir`, `create_grid_search_dir`, `resolve_keyed_param_grid`, `accumulate_variant_results`.

- **INIT:** `level_2/inference/__init__.py` — **Exports:** `VisionPredictor`.

- **INIT:** `level_2/models/__init__.py` — **Exports:** `DINOv2Model`, `BaseMultiOutputRegressionModel`, sklearn/boosting `get_*` lazy loaders, `TimmWeightLoader`.

- **INIT:** `level_2/progress/__init__.py` — **Exports:** `ProgressBarManager`, `ProgressMetrics`.

- **INIT:** `level_2/runtime/__init__.py` — **Exports:** `setup_runtime_environment`.

- **INIT:** `level_2/training/__init__.py` — **Exports:** `memory.__all__` plus trainer helpers (`ConfigHelper`, executors, factories, epoch helpers, etc.) — see source tuple.

- **INIT:** `level_2/training/memory/__init__.py` — **Exports:** `is_oom_error`, `recover_from_oom`, `cleanup_model`, `release_training_resources`.

- **INIT:** `level_2/validation/__init__.py` — **Exports:** `validate_*` helpers across arrays, dataframes, lists, series.

- **INIT:** `level_2/vision_transforms/__init__.py` — **Exports:** augmentation `__all__` plus `build_preprocessing_transforms`, `build_simple_transforms`, image cleaning, `PREPROCESSING_BUILDERS`, TTA API.

- **INIT:** `level_2/vision_transforms/augmentation/__init__.py` — **Exports:** preset + `AUGMENTATION_BUILDERS` surface.

---

## 4. Import Dependency Map

**INTERNAL IMPORTS SUMMARY:**

- **From level_0** (`layers.layer_0_core.level_0`): used throughout — logging/runtime (`get_logger`, `get_torch`, `get_config_value`, `is_kaggle`), errors (`DataValidationError`, `ConfigValidationError`, `ExecutionResult`), training hooks (`step_scheduler`, `create_history_entry`), vision constants (`IMAGENET_MEAN`, `IMAGENET_STD`), I/O helpers (`ensure_dir`), image helpers (`noise_reduction`, `get_image_size_from_config`), protein constants (`AA_ALPHABET`, k-mer lists, `HANDCRAFTED_FEATURE_DIM`, `extract_kmer_frequencies`), etc.

- **From level_1** (`layers.layer_0_core.level_1`): broad dependency — datasets, streaming, seeds; vision transforms and augmentation builders; training loop primitives, losses, AMP, checkpoints; validation helpers; grid execution; lazy sklearn; model bases (`BaseVisionModel`, `FiLM`, `BaseFeatureExtractor`); progress types; feature-cache path utilities; ensemble validation/weights; SigLIP helper; timm/HF cache configuration; CUDA cleanup helpers; etc.

- **Same-level (level_2):** relative imports in `__init__.py` files and intra-subpackage `.` imports only in package wiring; no `from level_2` package-root imports in logic modules.

- **Upward (level_3+):** none observed in `.py` under this tree.

---

## 5. FLAGS

- `level_2/models/dinov2_model.py` — 314 lines (above ~300-line note threshold).
- `level_2/training/memory/resource_cleanup.py` — 208 lines.
- `level_2/feature_extractors/cache_io.py` — 248 lines.
- `level_2/ensemble_strategies/averaging.py` — 233 lines.
- `level_2/inference/__init__.py` (7 lines), `level_2/runtime/__init__.py` (7 lines) — very small barrels.
- **Name overlap:** `extract_config_settings` as module function and `ConfigHelper.extract_config_settings` staticmethod; `process_batch` on both `TrainingPhaseExecutor` and `ValidationPhaseExecutor`.
- **Keyword scan:** `checkpointer.py` contains user-facing log text “incompatible” (checkpoint recovery). `semantic_features.py` mentions “SigLIP-compatible” in docstrings. No `deprecated`, `legacy`, `compat`, `backwards`, `TODO: remove`, or `shim` hits in `.py` sources.
- **Catch-all directory names:** none (`utils` / `helpers` / `misc` / `common` not present as package dirs).

---

## 6. Static scan summary (precheck)

- **Source:** `precheck_level_2_2026-04-08.md` — status **`skipped_machine_script`** (`ModuleNotFoundError: No module named 'torchvision'` in the environment that generated the precheck).
- No machine violation table; inventory reflects direct filesystem + AST review.

**Machine-generated (verify):** none (no `inventory_bootstrap_path`).
