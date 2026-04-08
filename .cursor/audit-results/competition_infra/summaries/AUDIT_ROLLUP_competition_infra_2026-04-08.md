---
generated: 2026-04-08
audit_scope: competition_infra
artifact_kind: rollup
audit_profile: full
audit_preset: single
run_mode: default
artifact_policy: regenerate
pass_number: 2
---

# Competition infra audit rollup (2026-04-08)

## USER_REQUEST (verbatim scope)

- Audit **competition infra**, **profile full**, **apply fixes**, **active overhaul**.
- Paths: `@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra` (duplicate line ignored).

## Targets audited (order)

`level_0`, `level_1`, `level_2`, `level_3`, `level_4`, `level_5`, `level_6` under `layer_1_competition/level_0_infra/`.

## Machine steps

- **Precheck:** `audit_precheck.py` run per tier; all reported `skipped_machine_script` / `ModuleNotFoundError: No module named 'level_0'` in this environment. Outputs: `summaries/precheck_level_*_2026-04-08.{md,json}`.
- **inventory_bootstrap.py:** Failed here (devtools → core import chain requires `level_0` on path + full deps). Audits used manual inventories.

## Policy update (pass 2)

- **Competition infra barrels:** `python-import-surfaces.mdc` now states explicitly that **`from layers…level_0_infra.level_J import …`** is correct for re-exported symbols **including** importers under `level_0_infra/level_J/`. **`code-audit-auditor.md`** Phase **7a-contest** clarifies this is **not** general-stack **`WRONG_LEVEL`**; misuse of deep paths when the barrel already exports is **`INFRA_DEEP_PATH`**.

## Code changes (pass 2, run_mode: default)

| File | Summary |
|------|---------|
| `level_0/paths/contest_output.py` | **`ContestPaths` via `level_0` package barrel** (`layers…level_0_infra.level_0`). |
| `level_1/contest/__init__.py` | Re-export **`load_training_csv`**, **`split_train_val`** before **`data_loading`**; extend **`__all__`**. |
| `level_1/contest/data_loading.py` | Single **`level_1` barrel** import for those four symbols plus existing **`layer_0_core`** imports. |
| `level_1/contest/csv_io.py` | Import order: **`import pandas as pd`** then **`from pathlib import Path`**; drop unused **`load_csv_raw_if_exists`**. |

## Artifact paths (`artifact_base` = `input/kaggle-ml-comp-scripts`)

- Inventories: `.cursor/audit-results/competition_infra/inventories/INVENTORY_level_{0..6}.md`
- Audits: `.cursor/audit-results/competition_infra/audits/level_{0..6}_audit.md`
- Precheck: `.cursor/audit-results/competition_infra/summaries/precheck_*_2026-04-08.md`

## Follow-ups (human / environment)

1. Run `python dev/scripts/audit_precheck.py` from `scripts/` in an environment where `path_bootstrap.prepend_framework_paths()` and `level_0` resolve (and optional deps like `torch` if required) to populate real static findings instead of skip stubs.
2. Full `pytest` / `validate_before_upload.py` when runtime deps are available (local import smoke test failed in this session on `layer_0_core` vision stack without `torch`).

## Counts (pass 2)

- **Tiers with repo edits:** 2 (`level_0`, `level_1`).
- **Python files touched:** 4 (`contest_output.py`, `contest/__init__.py`, `data_loading.py`, `csv_io.py`).

## Rules / agent docs touched

- `input/kaggle-ml-comp-scripts/.cursor/rules/python-import-surfaces.mdc`
- `input/kaggle-ml-comp-scripts/.cursor/rules/python-import-order.mdc` (Notes)
- Workspace `.cursor/agents/code-audit-auditor.md`
