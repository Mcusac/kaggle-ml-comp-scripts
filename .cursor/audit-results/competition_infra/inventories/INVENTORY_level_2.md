---
generated: 2026-03-31
scope: competition_infra
level: level_2
pass: 1
audit_profile: full
run_id: competition-infra-2026-03-31
level_path: C:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_0_infra\level_2
---

## 1. Package & File Tree

level_2/
  __init__.py  (package)
  README.md
  feature_extraction/
    __init__.py  (package)
    README.md
    helpers.py
    test_extractor.py
    trainer.py

## 2. Per-File Details

FILE: level_2/__init__.py
  Docstring: "Competition infra tier 2: feature-extraction trainer and regression submission."
  Classes:
    - (none)
  Functions:
    - (none)
  Imports:
    - from . import feature_extraction                                   [internal: competition_infra level_2]
    - from .feature_extraction import *                                   [internal: competition_infra level_2]
    - from layers.layer_1_competition.level_0_infra.level_3.submission import (create_regression_submission, expand_predictions_to_submission_format, save_submission)  [internal: competition_infra level_3]
  Line count: 20
  __all__: tuple(list(feature_extraction.__all__) + ["create_regression_submission", "expand_predictions_to_submission_format", "save_submission"])

FILE: level_2/feature_extraction/__init__.py
  Docstring: "Feature extraction training and test-time extraction."
  Classes:
    - (none)
  Functions:
    - (none)
  Imports:
    - from .helpers import FeatureExtractionConfigHelper, FeatureExtractionHelper  [internal: competition_infra level_2]
    - from .trainer import FeatureExtractionTrainer                               [internal: competition_infra level_2]
    - from .test_extractor import extract_test_features_from_model, find_feature_filename_from_ensemble_metadata  [internal: competition_infra level_2]
  Line count: 16
  __all__: ["FeatureExtractionConfigHelper", "FeatureExtractionHelper", "FeatureExtractionTrainer", "extract_test_features_from_model", "find_feature_filename_from_ensemble_metadata"]

FILE: level_2/feature_extraction/helpers.py
  Docstring: "Helpers for FeatureExtractionTrainer: config extraction and joint feature+target extraction."
  Classes:
    - FeatureExtractionConfigHelper
        Methods:
          - validate_inputs(config: Any, device: Any) -> None   [@staticmethod]
          - extract_dataset_type(config: Any) -> str            [@staticmethod]
          - extract_regression_model_type(config: Any) -> str   [@staticmethod]
          - extract_feature_extraction_model_name(config: Any) -> str  [@staticmethod]
    - FeatureExtractionHelper
        Methods:
          - __init__(self, feature_extractor: FeatureExtractor, dataset_type: str) -> None
          - extract_all_features(self, loader: Any) -> Tuple[np.ndarray, np.ndarray]
  Functions:
    - (none)
  Imports:
    - from typing import Any, Tuple                                       [stdlib]
    - import numpy as np                                                  [third-party]
    - from layers.layer_0_core.level_2 import FeatureExtractor             [internal: layer_0_core level_2]
    - from layers.layer_1_competition.level_0_infra.level_0 import get_dataset_type, get_feature_extraction_model_name, get_regression_model_type  [internal: competition_infra level_0]
    - from layers.layer_1_competition.level_0_infra.level_1 import validate_feature_extraction_inputs  [internal: competition_infra level_1]
  Line count: 48
  __all__: (not declared)

FILE: level_2/feature_extraction/trainer.py
  Docstring: "Feature extraction trainer for two-stage training. Uses level_0–level_3 and level_5 (save_regression_model)."
  Classes:
    - FeatureExtractionTrainer
        Methods:
          - __init__(self, config: Union[Any, Dict[str, Any]], device: torch.device, feature_extraction_model: Optional[nn.Module] = None, regression_model_hyperparameters: Optional[Dict[str, Any]] = None, regression_only: bool = False, metric_calculator: Optional[Any] = None, num_primary_targets: Optional[int] = None)
          - _setup_feature_extractor(self, config: Union[Any, Dict[str, Any]], device: torch.device, feature_extraction_model: Optional[nn.Module], regression_only: bool) -> Optional[FeatureExtractor]
          - _create_feature_extraction_model(self, model_name: str) -> nn.Module
          - extract_all_features(self, all_loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]
          - train(self, train_loader: Optional[DataLoader] = None, val_loader: Optional[DataLoader] = None, num_epochs: Optional[int] = None, save_dir: Optional[Path] = None, resume: bool = True, extract_features: bool = True, fold: Optional[int] = None, all_features: Optional[np.ndarray] = None, all_targets: Optional[np.ndarray] = None, fold_assignments: Optional[np.ndarray] = None) -> List[Dict]
  Functions:
    - (none)
  Imports:
    - import re                                                          [stdlib]
    - import numpy as np                                                 [third-party]
    - from pathlib import Path                                            [stdlib]
    - from typing import Any, Dict, List, Optional, Tuple, Union           [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch  [internal: layer_0_core level_0]
    - from layers.layer_0_core.level_1 import split_features_by_fold       [internal: layer_0_core level_1]
    - from layers.layer_0_core.level_2 import FeatureExtractor             [internal: layer_0_core level_2]
    - from layers.layer_0_core.level_3 import create_regression_model      [internal: layer_0_core level_3]
    - from layers.layer_0_core.level_5 import save_regression_model        [internal: layer_0_core level_5]
    - from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model  [internal: competition_infra level_1]
    - from layers.layer_1_competition.level_0_infra.level_2.feature_extraction.helpers import FeatureExtractionConfigHelper, FeatureExtractionHelper  [internal: competition_infra level_2]
  Line count: 189
  __all__: (not declared)

FILE: level_2/feature_extraction/test_extractor.py
  Docstring: "Generic test feature extraction for stacking and ensemble pipelines."
  Classes:
    - (none)
  Functions:
    - extract_test_features_from_model(test_csv_path: Path | str, data_root: str, dataset_type: str, config: Any, data_schema: Any, feature_extraction_model_name: str = "dinov2_base", batch_size: int = _DEFAULT_BATCH_SIZE, num_workers: int = 0) -> np.ndarray
    - find_feature_filename_from_ensemble_metadata(ensemble_configs: list, metadata_key: str = "model_paths") -> str
  Imports:
    - from pathlib import Path                                            [stdlib]
    - from typing import Any, Tuple                                       [stdlib]
    - import numpy as np                                                  [third-party]
    - from layers.layer_0_core.level_0 import get_logger                   [internal: layer_0_core level_0]
    - from layers.layer_0_core.level_1 import cleanup_gpu_memory, get_device  [internal: layer_0_core level_1]
    - from layers.layer_0_core.level_2 import FeatureExtractor             [internal: layer_0_core level_2]
    - from layers.layer_0_core.level_6 import create_test_dataloader       [internal: layer_0_core level_6]
    - from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model  [internal: competition_infra level_1]
    - from layers.layer_0_core.level_4 import load_json                    [internal: layer_0_core level_4]  (local import inside function)
  Line count: 122
  __all__: (not declared)

## 3. `__init__.py` Public API Summary

INIT: level_2/__init__.py
  Re-exports from:
    - level_2.feature_extraction (star import)
    - layers.layer_1_competition.level_0_infra.level_3.submission (selected functions)
  Exports (via `__all__`):
    - all symbols from `level_2.feature_extraction.__all__`
    - create_regression_submission
    - expand_predictions_to_submission_format
    - save_submission

INIT: level_2/feature_extraction/__init__.py
  Re-exports from:
    - level_2.feature_extraction.helpers (selected classes)
    - level_2.feature_extraction.trainer (selected class)
    - level_2.feature_extraction.test_extractor (selected functions)
  Exports (via `__all__`):
    - FeatureExtractionConfigHelper
    - FeatureExtractionHelper
    - FeatureExtractionTrainer
    - extract_test_features_from_model
    - find_feature_filename_from_ensemble_metadata

## 4. Import Dependency Map

INTERNAL IMPORTS (by source file):
  level_2/__init__.py:
    - layers.layer_1_competition.level_0_infra.level_3.submission (create_regression_submission, expand_predictions_to_submission_format, save_submission)
    - level_2.feature_extraction (package)
  level_2/feature_extraction/__init__.py:
    - level_2.feature_extraction.helpers (FeatureExtractionConfigHelper, FeatureExtractionHelper)
    - level_2.feature_extraction.trainer (FeatureExtractionTrainer)
    - level_2.feature_extraction.test_extractor (extract_test_features_from_model, find_feature_filename_from_ensemble_metadata)
  level_2/feature_extraction/helpers.py:
    - layers.layer_0_core.level_2 (FeatureExtractor)
    - layers.layer_1_competition.level_0_infra.level_0 (get_dataset_type, get_feature_extraction_model_name, get_regression_model_type)
    - layers.layer_1_competition.level_0_infra.level_1 (validate_feature_extraction_inputs)
  level_2/feature_extraction/trainer.py:
    - layers.layer_0_core.level_0 (ensure_dir, get_logger, get_torch)
    - layers.layer_0_core.level_1 (split_features_by_fold)
    - layers.layer_0_core.level_2 (FeatureExtractor)
    - layers.layer_0_core.level_3 (create_regression_model)
    - layers.layer_0_core.level_5 (save_regression_model)
    - layers.layer_1_competition.level_0_infra.level_1 (create_feature_extraction_model)
    - layers.layer_1_competition.level_0_infra.level_2.feature_extraction.helpers (FeatureExtractionConfigHelper, FeatureExtractionHelper)
  level_2/feature_extraction/test_extractor.py:
    - layers.layer_0_core.level_0 (get_logger)
    - layers.layer_0_core.level_1 (cleanup_gpu_memory, get_device)
    - layers.layer_0_core.level_2 (FeatureExtractor)
    - layers.layer_0_core.level_4 (load_json)  (import inside function)
    - layers.layer_0_core.level_6 (create_test_dataloader)
    - layers.layer_1_competition.level_0_infra.level_1 (create_feature_extraction_model)

NOTES (structure/style observed, not evaluated):
  - One `__init__.py` imports from competition infra level_3 (higher numeric tier).
  - Some files use deep module paths under `layers.*` (e.g., `...level_2.feature_extraction.helpers`).

## 5. Flags

FLAGS:
  - No files over 300 lines.
  - No files under 10 lines.
  - Keyword scan (deprecated/legacy/compat/backwards/TODO: remove/shim): no matches in `**/*.py`.
  - `level_2/__init__.py` imports from `layers.layer_1_competition.level_0_infra.level_3.*` (higher level).

