---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_5
pass_number: 1
artifact_kind: inventory
audit_profile: full
run_id: comp_infra_overhaul_2026-04-08
precheck_report_path: .cursor/audit-results/competition_infra/summaries/precheck_level_5_2026-04-08.md
level_path: scripts/layers/layer_1_competition/level_0_infra/level_5
---

#### INVENTORY: level_5

#### 1. Package & File Tree

```
level_5/
  __init__.py
  submission/
    __init__.py
    formatting.py
```

---

#### 2. Per-File Details

```
FILE: level_5/__init__.py
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
FILE: level_5/submission/__init__.py
  Classes:
    (none)
  Functions:
    (none)
  Imports:
    - from .formatting import expand_predictions_to_submission_format   [internal — same subpackage]
    - from layers.layer_0_core.level_5 import save_submission_csv        [internal — general stack level_5]
  Line count: 10
  __all__: ["expand_predictions_to_submission_format", "save_submission_csv"]
```

```
FILE: level_5/submission/formatting.py
  Classes:
    (none)
  Functions:
    - expand_predictions_to_submission_format(predictions: np.ndarray, test_csv_path: str, *, contest_config: Any, data_schema: Any, post_processor: Any) -> pd.DataFrame
  Imports:
    - import numpy as np                                           [third-party]
    - import pandas as pd                                          [third-party]
    - from pathlib import Path                                     [stdlib]
    - from typing import Any, Dict, List                           [stdlib]
    - from layers.layer_0_core.level_0 import get_logger           [internal — general stack level_0]
    - from layers.layer_0_core.level_5 import load_and_validate_test_data   [internal — general stack level_5]
  Line count: 61
  __all__: (not present)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_5/__init__.py
  Exports: (mirrors submission.__all__) expand_predictions_to_submission_format, save_submission_csv
  Re-exports from: level_5.submission (star import)
```

```
INIT: level_5/submission/__init__.py
  Exports: expand_predictions_to_submission_format, save_submission_csv
  Re-exports from: level_5.submission.formatting, layers.layer_0_core.level_5 (save_submission_csv)
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0:
    - get_logger — used in level_5/submission/formatting.py
  From layers.layer_0_core.level_5:
    - load_and_validate_test_data — used in level_5/submission/formatting.py
    - save_submission_csv — re-exported from level_5/submission/__init__.py
  From same competition_infra tier (level_5):
    - level_5/__init__.py: from . import submission; from .submission import * (barrel only)
    - level_5/submission/__init__.py: from .formatting import … (barrel only)
  From layers.layer_1_competition.level_0_infra.level_(N>5):
    - (none)
  Upward imports within infra (lower numeric tier ← higher): (none observed)
```

---

#### 5. Flags

```
FLAGS:
  level_5/__init__.py — 8 lines, thin barrel re-export only
  level_5/submission/__init__.py — 10 lines, thin barrel
  (no README.md in level_5 tree)
  (no catch-all package dirs: utils / helpers / misc / common)
  (no deprecated / legacy / compat / backwards / TODO: remove / shim tokens found)
  (no duplicate public function/class names across files in this level)
```

---

#### 6. Static scan summary (precheck)

Source: `precheck_level_5_2026-04-08.md` (machine hints; authoritative detail is §1–§5 above).

- **INFRA_TIER_UPWARD:** 0 file(s)
- **INFRA_GENERAL_LEVEL:** 0 file(s)
- **DEEP_PATH:** 0 file(s)
- **RELATIVE_IN_LOGIC:** 0 file(s)
- **PARSE_ERROR:** 0 file(s)
- **Clean files (per precheck):** `level_5/__init__.py`, `level_5/submission/__init__.py`, `level_5/submission/formatting.py`

---

#### Machine-generated (verify)

(not provided — no `inventory_bootstrap_path` for this run)
