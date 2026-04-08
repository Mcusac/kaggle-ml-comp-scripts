---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_3
pass_number: 1
run_id: comp_infra_overhaul_2026-04-08
artifact_kind: inventory
audit_profile: full
level_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_0_infra\level_3
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\competition_infra\summaries\precheck_level_3_2026-04-08.md
---

#### INVENTORY: `level_3`

#### 1. Package & File Tree

```
level_3/
  README.md
  __init__.py
  trainer/
    README.md
    __init__.py
    feature_extraction.py
```

---

#### 2. Per-File Details

```
FILE: level_3/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import trainer                               [internal]
    - from .trainer import *                              [internal]
  Line count: 8
  __all__: list(trainer.__all__) — resolves to ["FeatureExtractionTrainer"] given current trainer/__init__.py
```

```
FILE: level_3/trainer/__init__.py
  Module docstring: Trainer for contest pipelines. (notes re-export via level_2.feature_extraction)
  Classes: (none)
  Functions: (none)
  Imports:
    - from .feature_extraction import FeatureExtractionTrainer  [internal]
  Line count: 11
  __all__: ["FeatureExtractionTrainer"]
```

```
FILE: level_3/trainer/feature_extraction.py
  Module docstring: Feature extraction trainer for two-stage training. Uses level_0–level_3 and level_5 (save_regression_model).
  Classes:
    - FeatureExtractionTrainer
        Methods: __init__(self, config: Union[Any, Dict[str, Any]], device: torch.device, feature_extraction_model: Optional[nn.Module] = None, regression_model_hyperparameters: Optional[Dict[str, Any]] = None, regression_only: bool = False, metric_calculator: Optional[Any] = None, num_primary_targets: Optional[int] = None)
                 _setup_feature_extractor(self, config: Union[Any, Dict[str, Any]], device: torch.device, feature_extraction_model: Optional[nn.Module], regression_only: bool) -> Optional[FeatureExtractor]
                 _create_feature_extraction_model(self, model_name: str) -> nn.Module
                 extract_all_features(self, all_loader: DataLoader) -> Tuple[np.ndarray, np.ndarray]
                 train(self, train_loader: Optional[DataLoader] = None, val_loader: Optional[DataLoader] = None, num_epochs: Optional[int] = None, save_dir: Optional[Path] = None, resume: bool = True, extract_features: bool = True, fold: Optional[int] = None, all_features: Optional[np.ndarray] = None, all_targets: Optional[np.ndarray] = None, fold_assignments: Optional[np.ndarray] = None) -> List[Dict]
  Functions: (none at module level)
  Imports:
    - import re                                            [stdlib]
    - import numpy as np                                  [third_party]
    - from pathlib import Path                            [stdlib]
    - from typing import Any, Dict, List, Optional, Tuple, Union  [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_config_value, get_logger, get_torch  [internal — layer_0_core]
    - from layers.layer_0_core.level_1 import split_features_by_fold  [internal — layer_0_core]
    - from layers.layer_0_core.level_1.guards import validate_feature_extraction_trainer_inputs  [internal — layer_0_core]
    - from layers.layer_0_core.level_2 import FeatureExtractor, get_required_config_value  [internal — layer_0_core]
    - from layers.layer_0_core.level_3 import create_regression_model  [internal — layer_0_core]
    - from layers.layer_0_core.level_5 import save_regression_model  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model  [internal — competition_infra level_1]
    - from layers.layer_1_competition.level_0_infra.level_2 import FeatureExtractionHelper  [internal — competition_infra level_2]
  Line count: 193
  __all__: (none explicit)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_3/__init__.py
  Exports: FeatureExtractionTrainer (via trainer.__all__)
  Re-exports from: level_3.trainer
```

```
INIT: level_3/trainer/__init__.py
  Exports: FeatureExtractionTrainer
  Re-exports from: level_3.trainer.feature_extraction
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core:
    - level_0: ensure_dir, get_config_value, get_logger, get_torch
    - level_1: split_features_by_fold
    - level_1.guards: validate_feature_extraction_trainer_inputs
    - level_2: FeatureExtractor, get_required_config_value
    - level_3: create_regression_model
    - level_5: save_regression_model
  From layers.layer_1_competition.level_0_infra:
    - level_1: create_feature_extraction_model
    - level_2: FeatureExtractionHelper
  Relative in logic files: none (trainer/__init__.py uses relative import for aggregation)
  Upward within level_0_infra: none from this level’s modules (no imports from level_4+)
```

---

#### 5. Flags

```
FLAGS:
  level_3/trainer/feature_extraction.py — 193 lines (below 300-line threshold)
  level_3/__init__.py module docstring references “trainer factory and contest grid search”; `ContestGridSearchBase` / `build_grid_search_context` appear in level_3/README.md but not in any `.py` file under this tree (documentation vs code surface drift)
  level_3/README.md, level_3/trainer/README.md — describe `create_trainer` as imported from `level_3`; `create_trainer` is not exported by `level_3/__init__.py` in current code (auditor: align docs or exports)
```

---

#### 6. Static scan summary (precheck)

- **INFRA_TIER_UPWARD:** 0 files
- **INFRA_GENERAL_LEVEL:** 0 files
- **DEEP_PATH:** 0 files
- **RELATIVE_IN_LOGIC:** 0 files
- **PARSE_ERROR:** 0 files
- Precheck listed three Python modules under this scan root as clean files.
