---
generated: 2026-04-08
artifact_kind: audit_run_summary
audit_scope: competition_infra
audit_preset: single
audit_profile: full
run_mode: default
artifact_policy: regenerate
---

# Competition infra audit run summary

## USER_REQUEST (verbatim)

```
/code-audit 
audit competition infra
profile full
apply fixes
active overhaul

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra 
```

## Targets audited ( ascending )

`level_0` … `level_6` under `scripts/layers/layer_1_competition/level_0_infra/`.

## Machine steps

- **Precheck:** `dev/scripts/audit_precheck.py` per tier (`--audit-scope competition_infra`, `--date 2026-04-08`). Markdown regenerated so Phase 7 is not aligned to stale `skipped_machine_script` stubs.
- **Planner + auditor:** Full inventories under `inventories/INVENTORY_level_N.md` and audits under `audits/level_N_audit.md` for N = 0..6.

## Canonical artifacts

| Tier | Inventory | Audit |
|------|-----------|-------|
| 0 | `inventories/INVENTORY_level_0.md` | `audits/level_0_audit.md` |
| 1 | `inventories/INVENTORY_level_1.md` | `audits/level_1_audit.md` |
| 2 | `inventories/INVENTORY_level_2.md` | `audits/level_2_audit.md` |
| 3 | `inventories/INVENTORY_level_3.md` | `audits/level_3_audit.md` |
| 4 | `inventories/INVENTORY_level_4.md` | `audits/level_4_audit.md` |
| 5 | `inventories/INVENTORY_level_5.md` | `audits/level_5_audit.md` |
| 6 | `inventories/INVENTORY_level_6.md` | `audits/level_6_audit.md` |

## Highlights (applied fixes)

- **level_0:** `ContestPaths` via `level_0.contest` barrel; explicit `register_model_id_map`; `verify_export_output` optional `export_dir`; stub markers; README updates.
- **level_1:** `contest` barrel fixed (no missing `pipeline_shells`); `data_loading` cycle broken via submodule imports; path/model import surfaces; READMEs.
- **level_2:** Renamed `helpers.py` → `feature_extraction_helper.py`; import order; README corrections.
- **level_3 / level_4:** `create_trainer` ownership at **level_4**; init order `trainer` before `fold_orchestration`; CSIRO and factory call sites aligned; README drift fixed.
- **level_5:** README coverage for thin submission-formatting tier.
- **level_6:** General-stack import surfaces in `regression_submission.py`; READMEs.

## Follow-up (orchestrator)

- **`register_model_id_map()`** is invoked once when `level_1.registry.contest_registry` finishes loading so default infra `MODEL_ID_MAP` reaches core feature-cache naming before contest code runs; contest `registration.py` modules that call `set_model_id_map` still override afterward (e.g. CSIRO).

## Environment note

Full `import layers.layer_1_competition…` may still require **torch** / optional vision deps in `layer_0_core`; `compileall` on `level_0_infra` passed.

## Handoff

Use per-tier audit files for Phase 7 reconciliation with contest impl trees (`level_1_impl`).
