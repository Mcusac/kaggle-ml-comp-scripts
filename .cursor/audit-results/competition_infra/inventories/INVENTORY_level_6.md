---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_6
pass_number: 1
artifact_kind: inventory
audit_profile: full
run_id: comp_infra_overhaul_2026-04-08
precheck_report_path: .cursor/audit-results/competition_infra/summaries/precheck_level_6_2026-04-08.md
level_path: scripts/layers/layer_1_competition/level_0_infra/level_6
---

#### INVENTORY: level_6

#### 1. Package & File Tree

```
level_6/
  __init__.py
  submission/
    __init__.py
    regression_submission.py
```

---

#### 2. Per-File Details

```
FILE: level_6/__init__.py
  Classes:
    (none)
  Functions:
    (none)
  Imports:
    - from . import submission                                    [internal — same package]
    - from .submission import *                                    [internal — same package]
  Line count: 8
  __all__: list(submission.__all__)  (dynamic mirror of submission exports)
```

```
FILE: level_6/submission/__init__.py
  Classes:
    (none)
  Functions:
    (none)
  Imports:
    - from .regression_submission import create_regression_submission   [internal — same subpackage]
  Line count: 8
  __all__: ["create_regression_submission"]
```

```
FILE: level_6/submission/regression_submission.py
  Classes:
    (none)
  Functions:
    - _load_regression_model_from_path(regression_model_path: str) -> Any
    - create_regression_submission(regression_model_path: str, feature_extraction_model_name: str, test_csv_path: str, data_root: str, config: Any, device: Any, output_path: str, data_schema: Any, post_processor: Any) -> None
  Imports:
    - from typing import Any                                       [stdlib]
    - import numpy as np                                           [third-party]
    - from layers.layer_0_core.level_0 import get_logger           [internal — general stack level_0]
    - from layers.layer_0_core.level_4 import load_pickle          [internal — general stack level_4]
    - from layers.layer_0_core.level_5 import save_submission_csv   [internal — general stack level_5]
    - from layers.layer_1_competition.level_0_infra.level_2 import extract_test_features_from_model   [internal — competition infra level_2]
    - from layers.layer_1_competition.level_0_infra.level_5 import expand_predictions_to_submission_format   [internal — competition infra level_5]
  Line count: 67
  __all__: (not present)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_6/__init__.py
  Exports: (mirrors submission.__all__) create_regression_submission
  Re-exports from: level_6.submission (star import)
```

```
INIT: level_6/submission/__init__.py
  Exports: create_regression_submission
  Re-exports from: level_6.submission.regression_submission
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0:
    - get_logger — used in level_6/submission/regression_submission.py
  From layers.layer_0_core.level_4:
    - load_pickle — used in level_6/submission/regression_submission.py
  From layers.layer_0_core.level_5:
    - save_submission_csv — used in level_6/submission/regression_submission.py
  From layers.layer_1_competition.level_0_infra.level_2:
    - extract_test_features_from_model — used in level_6/submission/regression_submission.py
  From layers.layer_1_competition.level_0_infra.level_5:
    - expand_predictions_to_submission_format — used in level_6/submission/regression_submission.py
  From same competition_infra tier (level_6):
    - level_6/__init__.py: from . import submission; from .submission import * (barrel only)
    - level_6/submission/__init__.py: from .regression_submission import … (barrel only)
  From layers.layer_1_competition.level_0_infra.level_(N>6):
    - (none)
  Upward imports within infra (level_6 importing higher numeric infra tier): (none observed)
```

---

#### 5. Flags

```
FLAGS:
  level_6/__init__.py — 8 lines, thin barrel re-export only
  level_6/submission/__init__.py — 8 lines, thin barrel
  (no README.md in level_6 tree)
  (no catch-all package dirs: utils / helpers / misc / common)
  (no deprecated / legacy / compat / backwards / TODO: remove / shim tokens found)
  (no duplicate public function/class names across files in this level)
```

---

#### 6. Static scan summary (precheck)

Source: `precheck_level_6_2026-04-08.md` (machine hints; authoritative detail is §1–§5 above).

- **INFRA_TIER_UPWARD:** 0 file(s)
- **INFRA_GENERAL_LEVEL:** 0 file(s)
- **DEEP_PATH:** 0 file(s)
- **RELATIVE_IN_LOGIC:** 0 file(s)
- **PARSE_ERROR:** 0 file(s)
- **Clean files (per precheck):** `level_6/__init__.py`, `level_6/submission/__init__.py`, `level_6/submission/regression_submission.py`

---

#### Machine-generated (verify)

(not provided — no `inventory_bootstrap_path` for this run)
