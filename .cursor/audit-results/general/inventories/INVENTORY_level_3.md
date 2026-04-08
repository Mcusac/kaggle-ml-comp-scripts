---
generated: 2026-04-08
audit_scope: general
level_name: level_3
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_3_2026-04-08.md
---

# INVENTORY: level_3

#### 1. Package & File Tree

```
level_3/
  __init__.py
  README.md
  dataloader/
    __init__.py
    factory.py
    transforms.py
    README.md
  ensemble/
    __init__.py
    blending_ensemble.py
    create_meta_model.py
    per_target_weighted.py
    README.md
  ensemble_strategies/
    __init__.py
    handle_regression_ensemble_result.py
    handle_stacking_results.py
    pipeline_result_handler.py
  features/
    __init__.py
    extract_all_features.py
    handcrafted_feature_extraction.py
    siglip_extractor.py
    supervised_embedding_engine.py
    README.md
  metrics/
    __init__.py
    classification.py
    regression.py
    README.md
  runtime/
    __init__.py
    path_validation.py
    README.md
  training/
    __init__.py
    oom_retry.py
    sklearn_models.py
    timm_model.py
    tta_predictor.py
    README.md
  transforms/
    __init__.py
    factory.py
    README.md
  workflows/
    __init__.py
    progress_formatter.py
    train_test_pipeline.py
    README.md
```

---

#### 2. Per-File Details

```
FILE: level_3/__init__.py
  Module docstring: Level 3: Higher-level pipelines and composition (batch loading, transforms, evaluation, inference, training).
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import dataloader, ensemble_strategies, ensemble, features, metrics, runtime, training, transforms, workflows [internal]
    - from .dataloader import * [internal]
    - from .ensemble_strategies import * [internal]
    - from .ensemble import * [internal]
    - from .features import * [internal]
    - from .metrics import * [internal]
    - from .runtime import * [internal]
    - from .training import * [internal]
    - from .transforms import build_train_transform, build_tta_transforms, build_val_transform [internal]
    - from .workflows import * [internal]
  Line count: 38
  __all__: tuple expression — list(dataloader.__all__) + list(ensemble_strategies.__all__) + list(ensemble.__all__) + list(features.__all__) + list(metrics.__all__) + list(runtime.__all__) + list(training.__all__) + list(workflows.__all__) + ["build_train_transform", "build_val_transform", "build_tta_transforms"]
```

```
FILE: level_3/dataloader/__init__.py
  Module docstring: Dataloader package for level 3.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .factory import create_train_dataloader, create_val_dataloader [internal]
    - from .transforms import build_transforms_for_dataloaders [internal]
  Line count: 8
  __all__: ["create_train_dataloader", "create_val_dataloader", "build_transforms_for_dataloaders"]
```

```
FILE: level_3/dataloader/factory.py
  Module docstring: DataLoader factory for creating train/val dataloaders from config.
  Classes: (none)
  Functions:
    - _extract_loader_settings(config: Union[Any, Dict[str, Any]], batch_size: Optional[int], num_workers: Optional[int], pin_memory: Optional[bool]) -> Tuple[int, int, bool]
    - _extract_target_info(config: Union[Any, Dict[str, Any]]) -> Tuple[Optional[list], str]
    - _build_dataloader(data: pd.DataFrame, data_root: str, transform: Callable, dataset_type: str, batch_size: int, num_workers: int, pin_memory: bool, shuffle: bool, target_cols: Optional[list], image_path_column: str, **kwargs) -> DataLoader
    - _create_dataloader_from_config(data: pd.DataFrame, data_root: str, config: Union[Any, Dict[str, Any]], image_size: Tuple[int, int], transform: Optional[Callable], augmentation: AugmentationPreset, shuffle: bool, batch_size: Optional[int], dataset_type: str, num_workers: Optional[int], pin_memory: Optional[bool], **kwargs) -> DataLoader
    - create_train_dataloader(train_data: pd.DataFrame, data_root: str, config: Union[Any, Dict[str, Any]], image_size: Tuple[int, int], batch_size: Optional[int] = None, dataset_type: str = 'split', num_workers: Optional[int] = None, pin_memory: Optional[bool] = None, train_transform: Optional[Callable] = None, augmentation: AugmentationPreset = 'light', **kwargs) -> DataLoader
    - create_val_dataloader(val_data: pd.DataFrame, data_root: str, config: Union[Any, Dict[str, Any]], image_size: Tuple[int, int], batch_size: Optional[int] = None, dataset_type: str = 'split', num_workers: Optional[int] = None, pin_memory: Optional[bool] = None, val_transform: Optional[Callable] = None, **kwargs) -> DataLoader
  Imports:
    - import pandas as pd [third-party]
    - from typing import Any, Callable, Dict, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal]
    - from layers.layer_0_core.level_1 import StreamingDataset, StreamingSplitDataset [internal]
    - from layers.layer_0_core.level_2 import build_preprocessing_transforms, build_augmentation_transforms, AugmentationPreset [internal]
  Line count: 238
  __all__: (not defined at module level; exported via package __init__)
```

```
FILE: level_3/dataloader/transforms.py
  Module docstring: Transform builders for training and validation dataloaders.
  Classes: (none)
  Functions:
    - build_transforms_for_dataloaders(image_size: int, augmentation: AugmentationPreset, train_transform: Optional[Callable], val_transform: Optional[Callable]) -> Tuple[Callable, Callable]
  Imports:
    - from typing import Callable, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_2 import build_preprocessing_transforms, build_augmentation_transforms, AugmentationPreset [internal]
  Line count: 32
  __all__: (not defined at module level)
```

```
FILE: level_3/ensemble/__init__.py
  Module docstring: Ensemble utilities.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .blending_ensemble import blend_predictions, learn_blending_weights [internal]
    - from .create_meta_model import create_meta_model [internal]
    - from .per_target_weighted import PerTargetWeightedEnsemble [internal]
  Line count: 10
  __all__: ["blend_predictions", "learn_blending_weights", "create_meta_model", "PerTargetWeightedEnsemble"]
```

```
FILE: level_3/ensemble/blending_ensemble.py
  Module docstring: Blending ensemble: combine predictions with optional learned weights.
  Classes: (none)
  Functions:
    - _align_predictions(predictions_list: List[np.ndarray], padding_strategy: str = 'zeros') -> List[np.ndarray]
    - _pad_prediction(pred: np.ndarray, target_shape: tuple, method: str = 'zeros') -> np.ndarray
    - blend_predictions(predictions_list: List[np.ndarray], weights: Optional[List[float]] = None, method: str = 'weighted_average', power: float = 1.5, padding_strategy: str = 'zeros') -> np.ndarray
    - learn_blending_weights(predictions_list: List[np.ndarray], y_val: np.ndarray, method: str = 'ridge', alpha: float = 1.0) -> List[float]
    - _learn_weights_via_regression(features: np.ndarray, y_val: np.ndarray, n_targets: int, n_models: int, method: str, alpha: float) -> List[float]
    - _learn_weights_via_optimisation(predictions_list: List[np.ndarray], y_val: np.ndarray, n_models: int) -> List[float]
        (contains nested def _mse(w: np.ndarray) -> float)
  Imports:
    - import numpy as np [third-party]
    - from scipy.optimize import minimize [third-party]
    - from typing import List, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import get_ridge, get_linear_regression, weighted_average, geometric_mean, power_average [internal]
  Line count: 232
  __all__: (not defined at module level)
```

```
FILE: level_3/ensemble/create_meta_model.py
  Module docstring: Meta-model factory for stacking ensembles. (depends on level_2 sklearn loaders)
  Classes: (none)
  Functions:
    - create_meta_model(meta_model_type: str, meta_model_params: Optional[Dict[str, Any]], random_state: int) -> Any
  Imports:
    - from typing import Any, Dict, Optional [stdlib]
    - from layers.layer_0_core.level_2 import get_lasso, get_linear_regression, get_ridge [internal]
  Line count: 40
  __all__: (not defined at module level)
```

```
FILE: level_3/ensemble/per_target_weighted.py
  Module docstring: Per-target weighted ensemble: different weights for each target.
  Classes:
    - PerTargetWeightedEnsemble
        Methods:
          __init__(self, per_target_weights: Dict[str, List[float]], target_names: Optional[List[str]] = None, use_vectorized: bool = True) -> None
          combine(self, predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray
          get_name(self) -> str
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from typing import Dict, List, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, EnsemblingMethod, validate_predictions_list, get_shape_and_targets, combine_predictions_loop, combine_predictions_vectorized [internal]
    - from layers.layer_0_core.level_2 import build_weight_matrix [internal]
  Line count: 71
  __all__: (not defined at module level)
```

```
FILE: level_3/ensemble_strategies/__init__.py
  Module docstring: Ensemble result handlers composed above level_2.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .handle_regression_ensemble_result import handle_regression_ensemble_result [internal]
    - from .handle_stacking_results import handle_hybrid_stacking_result, handle_stacking_result [internal]
    - from .pipeline_result_handler import handle_ensemble_result [internal]
  Line count: 10
  __all__: ["handle_regression_ensemble_result", "handle_stacking_result", "handle_hybrid_stacking_result", "handle_ensemble_result"]
```

```
FILE: level_3/ensemble_strategies/handle_regression_ensemble_result.py
  Module docstring: Regression ensemble result handler.
  Classes: (none)
  Functions:
    - handle_regression_ensemble_result(returncode: int, stdout_lines: List[str], log_file: str, ensemble_config: Dict[str, Any]) -> None
  Imports:
    - from typing import Dict, Any, List [stdlib]
    - from layers.layer_0_core.level_2 import log_pipeline_completion [internal]
  Line count: 26
  __all__: (not defined at module level)
```

```
FILE: level_3/ensemble_strategies/handle_stacking_results.py
  Module docstring: Handles results from stacking pipeline execution.
  Classes: (none)
  Functions:
    - handle_stacking_result(returncode: int, stdout_lines: List[str], log_file: str, stacking_config: Dict[str, Any], operation_name: str = "Stacking pipeline") -> None
    - handle_hybrid_stacking_result(returncode: int, stdout_lines: List[str], log_file: str, hybrid_stacking_config: Dict[str, Any]) -> None
  Imports:
    - from typing import Any, Dict, List, Tuple [stdlib]
    - from layers.layer_0_core.level_2 import log_pipeline_completion [internal]
  Line count: 53
  __all__: (not defined at module level)
```

```
FILE: level_3/ensemble_strategies/pipeline_result_handler.py
  Module docstring: Ensemble pipeline result handler.
  Classes: (none)
  Functions:
    - handle_ensemble_result(returncode: int, stdout_lines: List[str], log_file: str, model_paths: List[str], method: str, score_type: str, model: str) -> None
  Imports:
    - from typing import List [stdlib]
    - from layers.layer_0_core.level_0 import is_kaggle [internal]
    - from layers.layer_0_core.level_1 import get_default_submission_csv_path [internal]
    - from layers.layer_0_core.level_2 import log_pipeline_completion [internal]
  Line count: 46
  __all__: (not defined at module level)
```

```
FILE: level_3/features/__init__.py
  Module docstring: Features sub-package.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .extract_all_features import extract_all_features [internal]
    - from .handcrafted_feature_extraction import extract_handcrafted_features_for_ids, extract_handcrafted_parallel, stream_features [internal]
    - from .siglip_extractor import SigLIPExtractor [internal]
    - from .supervised_embedding_engine import SupervisedEmbeddingEngine [internal]
  Line count: 17
  __all__: ["extract_all_features", "extract_handcrafted_features_for_ids", "extract_handcrafted_parallel", "stream_features", "SigLIPExtractor", "SupervisedEmbeddingEngine"]
```

```
FILE: level_3/features/extract_all_features.py
  Module docstring: Feature extraction utilities for two-stage training pipelines.
  Classes: (none)
  Functions:
    - extract_all_features(feature_extractor: FeatureExtractor, all_loader: DataLoader, dataset_type: str) -> Tuple[np.ndarray, np.ndarray]
    - _extract_targets(dataloader: DataLoader, dataset_type: str) -> np.ndarray
  Imports:
    - import numpy as np [third-party]
    - from typing import Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_torch [internal]
    - from layers.layer_0_core.level_2 import FeatureExtractor [internal]
  Line count: 52
  __all__: (not defined at module level)
```

```
FILE: level_3/features/handcrafted_feature_extraction.py
  Module docstring: Handcrafted feature extraction: sequential batch, parallel batch, and memory-safe streaming.
  Classes: (none)
  Functions:
    - _extract_one(pid: str, sequences: Dict[str, str]) -> np.ndarray
    - extract_handcrafted_features_for_ids(sequences: Dict[str, str], protein_ids: List[str]) -> np.ndarray
    - extract_handcrafted_parallel(sequences: Dict[str, str], protein_ids: List[str], max_workers: Optional[int] = None) -> np.ndarray
    - stream_features(sequences: Dict[str, str], chunk_size: Optional[int] = None) -> Generator[Tuple[np.ndarray, List[str]], None, None]
  Imports:
    - import os [stdlib]
    - import numpy as np [third-party]
    - from concurrent.futures import ThreadPoolExecutor [stdlib]
    - from typing import Dict, Generator, List, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, HANDCRAFTED_FEATURE_DIM [internal]
    - from layers.layer_0_core.level_2 import extract_handcrafted_features [internal]
  Line count: 98
  __all__: (not defined at module level)
```

```
FILE: level_3/features/siglip_extractor.py
  Module docstring: SigLIP embedding extractor.
  Classes:
    - SigLIPExtractor(BaseFeatureExtractor)
        Methods:
          __init__(self, model_path: str, model_name: Optional[str] = None, model_id: Optional[str] = None, model_resolver: Optional[ModelResolver] = None, device: Optional[torch.device] = None, patch_size: int = 520, overlap: int = 16) -> None
          extract_from_image(self, image: Union[np.ndarray, Image.Image, str, Path], return_patches: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, List[np.ndarray]]]
          extract_batch(self, images: List[Union[np.ndarray, Image.Image, str, Path]], show_progress: bool = True) -> np.ndarray
          extract_features(self, images: Union[List, np.ndarray, Image.Image, str, Path], **kwargs) -> np.ndarray
          save_to_cache(self, all_features: np.ndarray, all_targets: np.ndarray, fold_assignments: np.ndarray, combo_id: str = "combo_00", dataset_type: str = "split") -> None
  Functions:
    - _resolve_model_identity(model_path: str, model_name: Optional[str], model_id: Optional[str], model_resolver: Optional[ModelResolver]) -> Tuple[str, Optional[str]]
    - _load_siglip_components(model_path: str, device: torch.device, AutoModel: type, AutoImageProcessor: type) -> Tuple[Any, Any]
    - _detect_embedding_dim(model: Any) -> int
  Imports:
    - import numpy as np [third-party]
    - from PIL import Image [third-party]
    - from pathlib import Path [stdlib]
    - from typing import Any, Callable, List, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, get_torch, split_image, load_image_rgb [internal]
    - from layers.layer_0_core.level_1 import BaseFeatureExtractor, get_siglip_image_classes, generate_feature_filename [internal]
    - from layers.layer_0_core.level_2 import save_features [internal]
  Line count: 212
  __all__: (not defined at module level)
  Notes: ModelResolver = Callable[[str], Tuple[str, Optional[str]]]
```

```
FILE: level_3/features/supervised_embedding_engine.py
  Module docstring: Supervised embedding engine combining PCA, PLS, and GMM into a single feature pipeline.
  Classes:
    - SupervisedEmbeddingEngine
        Methods:
          __init__(self, n_pca: Union[int, float] = 0.80, n_pls: int = 8, n_gmm: int = 6, random_state: int = 42) -> None
          fit(self, X: np.ndarray, y: Optional[np.ndarray] = None, X_semantic: Optional[np.ndarray] = None) -> "SupervisedEmbeddingEngine"
          transform(self, X: np.ndarray, X_semantic: Optional[np.ndarray] = None) -> np.ndarray
          fit_transform(self, X: np.ndarray, y: Optional[np.ndarray] = None, X_semantic: Optional[np.ndarray] = None) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from typing import Optional, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import get_standard_scaler, get_pca, get_pls_regression, get_gaussian_mixture [internal]
  Line count: 133
  __all__: (not defined at module level)
```

```
FILE: level_3/metrics/__init__.py
  Module docstring: Metrics: classification and regression implementations; import triggers metric registration side effects.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .classification import (calculate_accuracy, calculate_f1, calculate_precision, calculate_recall, calculate_roc_auc, AccuracyMetric, F1Metric, PrecisionMetric, RecallMetric, ROCAUCMetric, calculate_classification_metrics, _register_classification_metrics) [internal]
    - from .regression import (calculate_rmse, calculate_mae, calculate_r2, calculate_r2_per_target, calculate_weighted_r2_from_arrays, prepare_weighted_arrays, calculate_weighted_rmse, RMSEMetric, MAEMetric, R2Metric, WeightedRMSEMetric, calculate_regression_metrics, _register_regression_metrics) [internal]
  Line count: 69
  __all__: ["calculate_accuracy", "calculate_f1", "calculate_precision", "calculate_recall", "calculate_roc_auc", "calculate_classification_metrics", "AccuracyMetric", "F1Metric", "PrecisionMetric", "RecallMetric", "ROCAUCMetric", "calculate_rmse", "calculate_mae", "calculate_r2", "calculate_r2_per_target", "calculate_weighted_r2_from_arrays", "prepare_weighted_arrays", "calculate_weighted_rmse", "calculate_regression_metrics", "RMSEMetric", "MAEMetric", "R2Metric", "WeightedRMSEMetric"]
  Notes: Calls _register_classification_metrics() and _register_regression_metrics() at import time.
```

```
FILE: level_3/metrics/classification.py
  Module docstring: Generic classification metrics (sklearn-backed).
  Classes:
    - AccuracyMetric(Metric): __init__(self); calculate(self, y_true, y_pred, sample_weight=None, **kwargs) -> float
    - F1Metric(Metric): __init__(self, average: str = "macro"); calculate(self, y_true, y_pred, **kwargs) -> float
    - PrecisionMetric(Metric): __init__(self, average: str = "macro"); calculate(self, y_true, y_pred, **kwargs) -> float
    - RecallMetric(Metric): __init__(self, average: str = "macro"); calculate(self, y_true, y_pred, **kwargs) -> float
    - ROCAUCMetric(Metric): __init__(self, average: str = "macro"); calculate(self, y_true, y_pred_proba, **kwargs) -> float
  Functions:
    - calculate_accuracy(y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> float
    - calculate_f1(y_true: np.ndarray, y_pred: np.ndarray, average: str = "macro") -> float
    - calculate_precision(y_true: np.ndarray, y_pred: np.ndarray, average: str = "macro") -> float
    - calculate_recall(y_true: np.ndarray, y_pred: np.ndarray, average: str = "macro") -> float
    - calculate_roc_auc(y_true: np.ndarray, y_pred_proba: np.ndarray, average: str = "macro", multi_class: str = "ovr") -> float
    - calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_pred_proba: Optional[np.ndarray] = None, average: str = "macro", sample_weight: Optional[np.ndarray] = None) -> Dict[str, float]
    - _register_classification_metrics() -> None
  Imports:
    - import numpy as np [third-party]
    - from typing import Dict, Optional [stdlib]
    - from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score, accuracy_score [third-party]
    - from layers.layer_0_core.level_0 import get_logger, Metric [internal]
    - from layers.layer_0_core.level_1 import register_metric [internal]
    - from layers.layer_0_core.level_2 import validate_paired_arrays [internal]
  Line count: 226
  __all__: (not defined at module level)
```

```
FILE: level_3/metrics/regression.py
  Module docstring: Generic regression metrics (sklearn-backed).
  Classes:
    - RMSEMetric(Metric): __init__(self); calculate(self, y_true, y_pred, sample_weight=None, **kwargs) -> float
    - MAEMetric(Metric): __init__(self); calculate(self, y_true, y_pred, sample_weight=None, **kwargs) -> float
    - R2Metric(Metric): __init__(self); calculate(self, y_true, y_pred, sample_weight=None, **kwargs) -> float
    - WeightedRMSEMetric(Metric): __init__(self); calculate(self, y_true, y_pred, target_weights=None, **kwargs) -> float
  Functions:
    - calculate_rmse(y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> float
    - calculate_mae(y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> float
    - calculate_r2(y_true: np.ndarray, y_pred: np.ndarray, sample_weight: Optional[np.ndarray] = None) -> float
    - calculate_r2_per_target(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray
    - prepare_weighted_arrays(y_true: np.ndarray, y_pred: np.ndarray, weights: Dict[str, float], target_order: List[str]) -> Tuple[np.ndarray, np.ndarray, np.ndarray]
    - calculate_weighted_r2_from_arrays(y_true_flat: np.ndarray, y_pred_flat: np.ndarray, weights_flat: np.ndarray) -> float
    - calculate_weighted_rmse(y_true: np.ndarray, y_pred: np.ndarray, target_weights: Optional[np.ndarray] = None) -> float
    - calculate_regression_metrics(y_true: np.ndarray, y_pred: np.ndarray, target_names: Optional[List[str]] = None, sample_weight: Optional[np.ndarray] = None) -> Dict[str, float]
    - _register_regression_metrics() -> None
  Imports:
    - import numpy as np [third-party]
    - from typing import Dict, List, Optional, Tuple [stdlib]
    - from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score as sklearn_r2_score [third-party]
    - from layers.layer_0_core.level_0 import get_logger, Metric [internal]
    - from layers.layer_0_core.level_1 import register_metric [internal]
    - from layers.layer_0_core.level_2 import validate_paired_arrays [internal]
  Line count: 243
  __all__: (not defined at module level)
```

```
FILE: level_3/runtime/__init__.py
  Module docstring: Runtime package for level 3.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .path_validation import validate_file_exists, validate_path_is_file, validate_image_path, validate_image_paths_in_dataframe [internal]
  Line count: 13
  __all__: ["validate_file_exists", "validate_path_is_file", "validate_image_path", "validate_image_paths_in_dataframe"]
```

```
FILE: level_3/runtime/path_validation.py
  Module docstring: Path validation. Validation utilities for file paths and image paths.
  Classes: (none)
  Functions:
    - validate_file_exists(path: Union[str, Path], name: str = "file") -> Path
    - validate_path_is_file(path: Union[str, Path], name: str = "file") -> Path
    - validate_image_path(path: Union[str, Path], check_exists: bool = True, name: str = "image") -> Path
    - validate_image_paths_in_dataframe(df: pd.DataFrame, image_column: str = 'image_path', check_exists: bool = False, max_missing_to_show: int = 10, name: str = "DataFrame") -> None
  Imports:
    - import pandas as pd [third-party]
    - from pathlib import Path [stdlib]
    - from typing import Union, List [stdlib]
    - from layers.layer_0_core.level_0 import DataValidationError [internal]
    - from layers.layer_0_core.level_2 import validate_dataframe, validate_column_values [internal]
  Line count: 170
  __all__: (not defined at module level)
```

```
FILE: level_3/training/__init__.py
  Module docstring: Training package for level 3.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .oom_retry import handle_oom_error_with_retry [internal]
    - from .sklearn_models import HistGradientBoostingRegressorModel, GradientBoostingRegressorModel, CatBoostRegressorModel, LGBMRegressorModel, XGBoostRegressorModel, RidgeRegressorModel, create_regression_model [internal]
    - from .timm_model import TimmModel [internal]
    - from .tta_predictor import TTAPredictor [internal]
  Line count: 25
  __all__: ["handle_oom_error_with_retry", "HistGradientBoostingRegressorModel", "GradientBoostingRegressorModel", "CatBoostRegressorModel", "LGBMRegressorModel", "XGBoostRegressorModel", "RidgeRegressorModel", "create_regression_model", "TimmModel", "TTAPredictor"]
```

```
FILE: level_3/training/oom_retry.py
  Module docstring: Generic OOM retry utilities.
  Classes: (none)
  Functions:
    - handle_oom_error_with_retry(func: Callable[..., Any], *args: Any, batch_size_key: str = "batch_size", initial_batch_size: Optional[int] = None, min_batch_size: int = 1, reduction_factor: float = 0.5, max_retries: int = 3, on_retry: Optional[Callable[[int], None]] = None, raise_on_failure: bool = True, **kwargs: Any) -> Any
  Imports:
    - from typing import Any, Callable, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal]
    - from layers.layer_0_core.level_2 import is_oom_error, recover_from_oom [internal]
  Line count: 98
  __all__: (not defined at module level)
```

```
FILE: level_3/training/sklearn_models.py
  Module docstring: Tabular/sklearn regression models for multi-output regression.
  Classes:
    - HistGradientBoostingRegressorModel(BaseMultiOutputRegressionModel): _get_model_class(self); _get_default_params(self); _get_model_name(self)
    - GradientBoostingRegressorModel(BaseMultiOutputRegressionModel): _get_model_class(self); _get_default_params(self); _get_model_name(self)
    - CatBoostRegressorModel(BaseMultiOutputRegressionModel): _get_model_class(self); _get_default_params(self); _get_model_name(self)
    - LGBMRegressorModel(BaseMultiOutputRegressionModel): _get_model_class(self); _get_default_params(self); _get_model_name(self)
    - XGBoostRegressorModel(BaseMultiOutputRegressionModel): _get_model_class(self); _get_default_params(self); _get_model_name(self)
    - RidgeRegressorModel(BaseMultiOutputRegressionModel): _get_model_class(self); _get_default_params(self); _get_model_name(self)
  Functions:
    - create_regression_model(model_type: str, **params)
  Imports:
    - from layers.layer_0_core.level_2 import get_gradient_boosting_regressor, get_catboost, get_lightgbm, get_xgboost, get_ridge, BaseMultiOutputRegressionModel [internal]
  Line count: 136
  __all__: (not defined at module level)
```

```
FILE: level_3/training/timm_model.py
  Module docstring: Wrapper for timm models with configurable output head.
  Classes:
    - TimmModel(BaseVisionModel)
        Methods:
          _validate_init_params(self, model_name: str, num_classes: int, input_size: Optional[Tuple[int, int]]) -> None
          _create_backbone(self, model_name: str, pretrained: bool) -> tuple
          _extract_feature_dimension(self, backbone: Any) -> int
          _create_regression_heads(self, num_classes: int) -> None
          _extract_input_size(self, backbone: Any, input_size: Optional[Tuple[int, int]]) -> Tuple[int, int]
          __init__(self, model_name: str = "efficientnet_b0", pretrained: bool = True, num_classes: int = 1, input_size: Optional[Tuple[int, int]] = None, dataset_type: DatasetType = 'single') -> None
          forward(self, x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]) -> torch.Tensor
          get_input_size(self) -> Tuple[int, int]
          freeze_backbone(self) -> None
          unfreeze_backbone(self) -> None
          is_pretrained(self) -> bool
  Functions: (none)
  Module-level: DEFAULT_IMAGE_SIZE: Tuple[int, int] = (224, 224); DatasetType = Literal['single', 'split']
  Imports:
    - from typing import Any, Literal, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal]
    - from layers.layer_0_core.level_1 import BaseVisionModel [internal]
    - from layers.layer_0_core.level_2 import TimmWeightLoader [internal]
  Line count: 210
  __all__: (not defined at module level)
```

```
FILE: level_3/training/tta_predictor.py
  Module docstring: Test-time augmentation predictor.
  Classes:
    - TTAPredictor
        Methods:
          __init__(self, model: nn.Module, device: torch.device, image_size: int = 224, tta_variants: Optional[List[Union[TTAVariant, str]]] = None, use_mixed_precision: bool = False) -> None
          predict(self, dataloader: DataLoader, verbose: bool = True) -> np.ndarray  (@torch.no_grad())
          predict_single_image(self, image: torch.Tensor, pil_image: Optional[Image.Image] = None) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from PIL import Image [third-party]
    - from typing import List, Optional, Union [stdlib]
    - from tqdm import tqdm [third-party]
    - from layers.layer_0_core.level_0 import get_logger, get_torch [internal]
    - from layers.layer_0_core.level_1 import forward_with_amp [internal]
    - from layers.layer_0_core.level_2 import build_tta_transforms, TTAVariant [internal]
  Line count: 115
  __all__: (not defined at module level)
```

```
FILE: level_3/transforms/__init__.py
  Module docstring: Config-driven transform factory. Bridges config objects to level_2 vision transforms.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .factory import build_train_transform, build_val_transform, build_tta_transforms [internal]
  Line count: 11
  __all__: ["build_train_transform", "build_val_transform", "build_tta_transforms"]
```

```
FILE: level_3/transforms/factory.py
  Module docstring: Config-driven transform factory. Bridges config objects to level_2 vision transforms.
  Classes: (none)
  Functions:
    - _build_deterministic_augmentations_from_list(augmentation_list: List[str]) -> Tuple[List[Any], List[Any]]
    - _build_preprocessing_transforms_from_config(config: Union[Any, dict], preprocessing_list: List[str]) -> List[Any]
    - _build_augmentation_transforms_from_config(config: Union[Any, dict], augmentation_list: List[str], include_augmentation: bool) -> Tuple[List[Any], List[Any]]
    - _build_tensor_transforms(config: Union[Any, dict]) -> List[Any]
    - _build_base_transform(config: Union[Any, dict], include_augmentation: bool = False) -> transforms.Compose
    - build_train_transform(config: Union[Any, dict]) -> transforms.Compose
    - build_val_transform(config: Union[Any, dict]) -> transforms.Compose
    - _apply_geometric_variant(variant: str, variant_pil_transforms: List) -> None
    - _apply_deterministic_augmentations(augmentation_list: List[str], variant_pil_transforms: List, variant_tensor_transforms: List) -> None
    - _build_single_tta_variant(variant: str, base_pil_transforms: List, augmentation_list: List[str], config: Union[Any, dict]) -> transforms.Compose
    - build_tta_transforms(config: Union[Any, dict], tta_variants: Optional[List[str]] = None) -> List[transforms.Compose]
  Imports:
    - import torchvision.transforms as transforms [third-party]
    - from typing import Any, List, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import DEFAULT_BLUR_SIGMA, DEFAULT_COLOR_BRIGHTNESS, DEFAULT_COLOR_CONTRAST, DEFAULT_COLOR_HUE, DEFAULT_COLOR_SATURATION, DEFAULT_TTA_VARIANTS, AVAILABLE_TTA_VARIANTS, IMAGENET_MEAN, IMAGENET_STD, get_image_size_from_config, get_logger [internal]
    - from layers.layer_0_core.level_1 import compose_transform_pipeline, get_color_jitter_transform, get_noise_transform, get_normalize_transform, get_resize_transform [internal]
    - from layers.layer_0_core.level_2 import PREPROCESSING_BUILDERS, build_augmentation_transforms [internal]
  Line count: 237
  __all__: (not defined at module level)
```

```
FILE: level_3/workflows/__init__.py
  Module docstring: Workflows package for level 3.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .progress_formatter import ProgressFormatter [internal]
    - from .train_test_pipeline import train_test_pipeline [internal]
  Line count: 7
  __all__: ["ProgressFormatter", "train_test_pipeline"]
```

```
FILE: level_3/workflows/progress_formatter.py
  Module docstring: Formats progress bar output and metrics display (multi-line).
  Classes:
    - ProgressFormatter
        Methods:
          __init__(self, config: ProgressConfig) -> None
          format_time(seconds: float) -> str  (@staticmethod)
          format_postfix(self, bar_id: str, metrics: "ProgressMetrics", current: int, total: Optional[int] = None, unit: str = "it", **metrics_kwargs: Any) -> Dict[str, Any]
  Functions: (none)
  Imports:
    - from typing import Dict, Any, Optional [stdlib]
    - from layers.layer_0_core.level_1 import ProgressConfig, ProgressVerbosity [internal]
    - from layers.layer_0_core.level_2 import ProgressMetrics [internal]
  Line count: 71
  __all__: (not defined at module level)
```

```
FILE: level_3/workflows/train_test_pipeline.py
  Module docstring: Train-test pipeline. Requires contest_context and train_pipeline_fn from contest.
  Classes: (none)
  Functions:
    - train_test_pipeline(contest_context: Any, train_pipeline_fn: Optional[Any] = None, data_root: Optional[str] = None, model: Optional[str] = None, **kwargs) -> None
  Imports:
    - from typing import Optional, Any [stdlib]
    - from layers.layer_0_core.level_0 import get_fold_checkpoint_path, get_logger [internal]
    - from layers.layer_0_core.level_2 import find_best_fold_from_scores [internal]
  Line count: 64
  __all__: (not defined at module level)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_3/__init__.py
  Exports: union of dataloader, ensemble_strategies, ensemble, features, metrics, runtime, training, workflows __all__ symbols, plus build_train_transform, build_val_transform, build_tta_transforms from transforms (transforms subpackage __all__ is also those three names).
  Re-exports from: level_3.dataloader, level_3.ensemble_strategies, level_3.ensemble, level_3.features, level_3.metrics, level_3.runtime, level_3.training, level_3.transforms (partial), level_3.workflows
```

```
INIT: level_3/dataloader/__init__.py
  Exports: create_train_dataloader, create_val_dataloader, build_transforms_for_dataloaders
  Re-exports from: level_3.dataloader.factory, level_3.dataloader.transforms
```

```
INIT: level_3/ensemble/__init__.py
  Exports: blend_predictions, learn_blending_weights, create_meta_model, PerTargetWeightedEnsemble
  Re-exports from: level_3.ensemble.blending_ensemble, level_3.ensemble.create_meta_model, level_3.ensemble.per_target_weighted
```

```
INIT: level_3/ensemble_strategies/__init__.py
  Exports: handle_regression_ensemble_result, handle_stacking_result, handle_hybrid_stacking_result, handle_ensemble_result
  Re-exports from: level_3.ensemble_strategies.handle_regression_ensemble_result, level_3.ensemble_strategies.handle_stacking_results, level_3.ensemble_strategies.pipeline_result_handler
```

```
INIT: level_3/features/__init__.py
  Exports: extract_all_features, extract_handcrafted_features_for_ids, extract_handcrafted_parallel, stream_features, SigLIPExtractor, SupervisedEmbeddingEngine
  Re-exports from: level_3.features.extract_all_features, level_3.features.handcrafted_feature_extraction, level_3.features.siglip_extractor, level_3.features.supervised_embedding_engine
```

```
INIT: level_3/metrics/__init__.py
  Exports: (see __all__ in §2 — classification + regression public functions and Metric classes; does not export _register_* )
  Re-exports from: level_3.metrics.classification, level_3.metrics.regression
  Side effects: _register_classification_metrics(); _register_regression_metrics()
```

```
INIT: level_3/runtime/__init__.py
  Exports: validate_file_exists, validate_path_is_file, validate_image_path, validate_image_paths_in_dataframe
  Re-exports from: level_3.runtime.path_validation
```

```
INIT: level_3/training/__init__.py
  Exports: handle_oom_error_with_retry, HistGradientBoostingRegressorModel, GradientBoostingRegressorModel, CatBoostRegressorModel, LGBMRegressorModel, XGBoostRegressorModel, RidgeRegressorModel, create_regression_model, TimmModel, TTAPredictor
  Re-exports from: level_3.training.oom_retry, level_3.training.sklearn_models, level_3.training.timm_model, level_3.training.tta_predictor
```

```
INIT: level_3/transforms/__init__.py
  Exports: build_train_transform, build_val_transform, build_tta_transforms
  Re-exports from: level_3.transforms.factory
```

```
INIT: level_3/workflows/__init__.py
  Exports: ProgressFormatter, train_test_pipeline
  Re-exports from: level_3.workflows.progress_formatter, level_3.workflows.train_test_pipeline
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From level_0 .. level_(N-1) with N=3 — all logic files use absolute package form `from layers.layer_0_core.level_<k> import ...` with k in {0,1,2} only.
    level_0 (observed symbols): get_logger, get_torch, DataValidationError, DEFAULT_BLUR_SIGMA, DEFAULT_COLOR_BRIGHTNESS, DEFAULT_COLOR_CONTRAST, DEFAULT_COLOR_HUE, DEFAULT_COLOR_SATURATION, DEFAULT_TTA_VARIANTS, AVAILABLE_TTA_VARIANTS, IMAGENET_MEAN, IMAGENET_STD, get_image_size_from_config, get_fold_checkpoint_path, Metric, EnsemblingMethod, validate_predictions_list, get_shape_and_targets, combine_predictions_loop, combine_predictions_vectorized, HANDCRAFTED_FEATURE_DIM, split_image, load_image_rgb, is_kaggle
    level_1 (observed symbols): compose_transform_pipeline, get_color_jitter_transform, get_noise_transform, get_normalize_transform, get_resize_transform, ProgressConfig, ProgressVerbosity, forward_with_amp, BaseVisionModel, StreamingDataset, StreamingSplitDataset, BaseFeatureExtractor, get_siglip_image_classes, generate_feature_filename, register_metric, get_default_submission_csv_path
    level_2 (observed symbols): build_preprocessing_transforms, build_augmentation_transforms, AugmentationPreset, log_pipeline_completion, find_best_fold_from_scores, ProgressMetrics, PREPROCESSING_BUILDERS, build_tta_transforms, TTAVariant, TimmWeightLoader, get_gradient_boosting_regressor, get_catboost, get_lightgbm, get_xgboost, get_ridge, BaseMultiOutputRegressionModel, is_oom_error, recover_from_oom, validate_dataframe, validate_column_values, validate_paired_arrays, get_standard_scaler, get_pca, get_pls_regression, get_gaussian_mixture, save_features, extract_handcrafted_features, FeatureExtractor, build_weight_matrix, get_lasso, get_linear_regression, weighted_average, geometric_mean, power_average

  From same level (level_3) in a logic file:
    `from level_3 import ...` — not observed
    `from layers.layer_0_core.level_3...` — not observed in .py files under level_3
    `from .` / `from ..` — observed only under __init__.py files (subpackage aggregation)

  From level_(N+1) or higher (general stack): not observed
```

---

#### 5. Flags

```
FLAGS:
  level_3/ensemble_strategies/pipeline_result_handler.py — import is_kaggle from level_0 present; symbol not referenced in module body (possible unused import)
  level_3/dataloader/factory.py — line count 238; level_3/transforms/factory.py — line count 237; level_3/ensemble/blending_ensemble.py — line count 232; level_3/metrics/classification.py — 226 (largest modules in tier; none exceed 300 lines by current count)
  level_3/transforms/factory.py and level_3/dataloader/factory.py — both named factory.py under different subpackages (name collision at search/navigation level only)
  level_3/workflows/__init__.py — 7 lines; level_3/dataloader/__init__.py — 8 lines (minimal barrels)
  level_3/metrics/__init__.py — import-time registration side effects (_register_classification_metrics, _register_regression_metrics)
  Multiple public functions named handle_* in ensemble_strategies (distinct modules; shared prefix)
```

---

#### 6. Static scan summary (optional)

Source: `precheck_level_3_2026-04-08.md`

- **precheck_status:** skipped_machine_script
- **Reason:** `ModuleNotFoundError: No module named 'torchvision'` — environment could not import the devtools precheck stack.
- **Impact:** Machine Phase 7 / automated reconciliation from `audit_precheck.py` not available for this run; inventory relies on manual tree walk only.

**Machine-generated (verify):** (not provided — no `inventory_bootstrap_path`)
