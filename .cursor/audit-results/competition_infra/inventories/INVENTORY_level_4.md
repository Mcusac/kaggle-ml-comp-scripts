---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_4
pass_number: 1
run_id: comp_infra_overhaul_2026-04-08
artifact_kind: inventory
audit_profile: full
level_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_0_infra\level_4
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\competition_infra\summaries\precheck_level_4_2026-04-08.md
---

#### INVENTORY: `level_4`

#### 1. Package & File Tree

```
level_4/
  README.md
  __init__.py
  fold_orchestration/
    README.md
    __init__.py
    single_fold.py
  trainer/
    README.md
    __init__.py
    factory.py
```

---

#### 2. Per-File Details

```
FILE: level_4/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import fold_orchestration, trainer          [internal]
    - from .fold_orchestration import *                  [internal]
    - from .trainer import *                             [internal]
  Line count: 11
  __all__: list(fold_orchestration.__all__) + list(trainer.__all__) — resolves to ["train_single_fold", "create_trainer"] given current subpackages
```

```
FILE: level_4/trainer/__init__.py
  Module docstring: Trainer for contest pipelines.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .factory import create_trainer                 [internal]
  Line count: 7
  __all__: ["create_trainer"]
```

```
FILE: level_4/trainer/factory.py
  Module docstring: Trainer factory for creating appropriate trainer instances.
  Classes: (none)
  Functions:
    - create_trainer(config: Any, device: Any, model: Optional[Any] = None, regression_model_hyperparameters: Optional[Dict[str, Any]] = None, regression_only: bool = False, metric_calculator: Optional[Any] = None) -> Union[BaseModelTrainer, FeatureExtractionTrainer]
  Imports:
    - from typing import Optional, Dict, Any, Union       [stdlib]
    - from layers.layer_0_core.level_0 import get_config_value, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_5 import BaseModelTrainer  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_3.trainer import FeatureExtractionTrainer  [internal — competition_infra level_3]
  Line count: 44
  __all__: (none explicit)
```

```
FILE: level_4/fold_orchestration/__init__.py
  Module docstring: Fold orchestration — coordinates trainer and dataloader creation for a single CV fold.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .single_fold import train_single_fold          [internal]
  Line count: 5
  __all__: ["train_single_fold"]
```

```
FILE: level_4/fold_orchestration/single_fold.py
  Module docstring: Train a single CV fold: trainer, dataloaders, and train loop.
  Classes: (none)
  Functions:
    - train_single_fold(fold: int, n_folds: int, train_data: Any, val_data: Any, data_root: str, config: Any, image_size: Tuple[int, int], num_epochs: int, dataset_type: str, model_dir: Path, metric_calculator: Any = None) -> float
  Imports:
    - from pathlib import Path                          [stdlib]
    - from typing import Any, Tuple                     [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_1 import cleanup_gpu_memory, get_device  [internal — layer_0_core]
    - from layers.layer_0_core.level_3 import create_train_dataloader, create_val_dataloader  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_3 import create_trainer  [internal — competition_infra level_3]
  Line count: 93
  __all__: (none explicit)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_4/__init__.py
  Exports: train_single_fold, create_trainer (combined submodule __all__)
  Re-exports from: level_4.fold_orchestration, level_4.trainer
```

```
INIT: level_4/trainer/__init__.py
  Exports: create_trainer
  Re-exports from: level_4.trainer.factory
```

```
INIT: level_4/fold_orchestration/__init__.py
  Exports: train_single_fold
  Re-exports from: level_4.fold_orchestration.single_fold
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core:
    - level_0: ensure_dir, get_logger (single_fold); get_config_value, get_logger (factory)
    - level_1: cleanup_gpu_memory, get_device
    - level_3: create_train_dataloader, create_val_dataloader
    - level_5: BaseModelTrainer
  From layers.layer_1_competition.level_0_infra:
    - level_3: create_trainer (single_fold only)
    - level_3.trainer: FeatureExtractionTrainer (factory only)
  Relative in logic files: none
  Infra tier note: level_4 factory imports level_3.trainer.FeatureExtractionTrainer (lower infra tier from higher tier package); single_fold imports create_trainer from package level_3 root
```

---

#### 5. Flags

```
FLAGS:
  level_4/fold_orchestration/single_fold.py — imports `create_trainer` from `layers.layer_1_competition.level_0_infra.level_3`; `level_3/__init__.py` only exposes `FeatureExtractionTrainer` in `__all__` while `create_trainer` is implemented in `level_4/trainer/factory.py` (potential import/export mismatch for auditor)
  level_4/README.md, level_4/trainer/README.md, level_4/fold_orchestration/README.md — present (non-Python)
```

---

#### 6. Static scan summary (precheck)

- **INFRA_TIER_UPWARD:** 0 files
- **INFRA_GENERAL_LEVEL:** 0 files
- **DEEP_PATH:** 0 files
- **RELATIVE_IN_LOGIC:** 0 files
- **PARSE_ERROR:** 0 files
- Precheck listed four Python modules under this scan root as clean files.
