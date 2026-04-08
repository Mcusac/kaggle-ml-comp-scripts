---
generated: 2026-04-08
audit_scope: general
level_name: level_7
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_7_2026-04-08.md
---

# Audit: level_7

## Phase 1 — Functions & Classes

Reviewed inventory modules: factories and grid_search helpers are focused; `HyperparameterGridSearchBase` correctly extends `GridSearchBase`; private helpers in `dataset_variant_executor` stay scoped to variant execution.

**Change log:** None required beyond import-surface alignment (no renames).

## Phase 2 — Files

No split/merge: file sizes and cohesion are acceptable (`dataset_variant_executor` is the largest but single-purpose).

**Change log:** None.

## Phase 3 — Packages & Sub-packages

Structure is concept-based (`factories/`, `grid_search/`). No root-level logic `.py` besides `__init__.py`.

**Change log:** None.

## Phase 4 — Legacy & Compatibility

No deprecation shims, compat branches, or stale markers found.

**Change log:** `No legacy or compatibility code found.`

## Phase 5 — Full Level Review

- Names and vocabulary are consistent.
- Dependencies within level_7: init-only relatives; logic files depend only on lower levels after edits.
- Root `__init__.py` re-exports match `__all__`.

**Dependency rule (general):** All logic imports target `level_0`–`level_6` only; no same-level `from level_7` in logic files; no upward imports.

## Phase 6 — README & Documentation

**Change log:**

- `level_7/README.md` :: README updated :: Corrected dependency bullets (removed stale level_5/grid claims); documented `cleanup_gpu_memory`; completed public API table (`get_completed_count`, `run_variant_cleanup`, `run_final_cleanup`).
- `level_7/grid_search/README.md` :: README updated :: Dropped incorrect level_5 dependency; aligned bullets to actual imports.

## Phase 7 — Cross-Level Audit

**Precheck:** `precheck_level_7_2026-04-08.md` reported `skipped_machine_script` (`torchvision` missing). No machine violation list to reconcile; structural import fixes were applied from policy.

**7a — Import enforcement (general, N=7):**

- Replaced `from layers.layer_0_core.level_K import …` with **`from level_K import …`** in all logic files under `level_7`, per `python-import-surfaces.mdc` and import-order grouping (stdlib → `level_*`).
- **`__init__.py` files** unchanged except `grid_search/__init__.py` (still uses relative aggregation for siblings; `from level_6 import …` for lower-level public API).

**Violation log (resolved in-repo):**

| File | Before | Violation | Action |
|------|--------|-----------|--------|
| `factories/tabular_model_factory.py` | `layers.layer_0_core.level_5/6` | Non–public-surface general imports | Use `from level_5` / `from level_6` |
| `factories/create_ensembling_method.py` | `layers.layer_0_core.level_0/3/6` | Same | Use `from level_0`, `level_3`, `level_6` |
| `grid_search/__init__.py` | `layers.layer_0_core.level_6` | Same | Use `from level_6` |
| `grid_search/dataset_variant_executor.py` | `layers.layer_0_core.level_*` | Same | Use `from level_0`, `level_1`, `level_6` |
| `grid_search/hyperparameter_base.py` | `layers.layer_0_core.level_*` | Same | Use `from level_0`, `level_6` |
| `grid_search/variant_result_builders.py` | `layers.layer_0_core.level_*` | Same | Use `from level_0`, `level_6` |

**Caller import bug (not exported from level_7):**

- `layers/.../level_csiro/level_2/regression_ensemble_pipeline.py` imported `create_regression_ensemble_from_paths` from **level_7**; symbol is defined under **level_8**. Updated to `layers.layer_0_core.level_8`.

**7b–7d:** No DRY/SOLID/KISS issues requiring downward consolidation beyond existing use of `level_6` grid helpers.

---

## Phase 8 — Callers

**CALLERS UPDATED:**

- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_2/regression_ensemble_pipeline.py` :: `create_regression_ensemble_from_paths` import `level_7` → `level_8`.

Public names on `level_7` unchanged; other `from layers.layer_0_core.level_7 import …` call sites need no edit.

---

```
=== AUDIT RESULT: level_7 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):
  calculate_focused_grid_size — focused grid sizing (re-export from level_6)
  auto_detect_grid_search_results — locate grid-search results files (re-export from level_6)
  get_completed_count — count completed variants (re-export from level_6)
  build_success_result — success variant result dict for hyperparameter/regression grids
  build_error_result — error variant result dict
  create_ensembling_method — factory for ensembling methods by name
  HyperparameterGridSearchBase — base class extending level_6 GridSearchBase
  run_single_variant — run one dataset grid-search variant (injected train pipeline)
  run_variant_cleanup — per-variant cleanup (re-export from level_6)
  run_final_cleanup — post-grid cleanup (re-export from level_6)
  create_tabular_model — factory for tabular models by type string

CONSOLIDATED CHANGE LOG:
  Phase 1: 0 changes
  Phase 2: 0 changes
  Phase 3: 0 changes
  Phase 4: 0 changes
  Phase 5: 0 (holistic review only)
  Phase 6: 2 READMEs updated (level_7, level_7/grid_search)
  Phase 7: 6 logic/init files normalized to `from level_K` imports; 1 CSIRO caller import corrected to level_8
  Phase 8: 1 caller file (regression_ensemble_pipeline.py)

  Itemized:
  - factories/tabular_model_factory.py — `from level_5`, `from level_6`; sorted imported model names
  - factories/create_ensembling_method.py — `from level_0`, `level_3`, `level_6`; sorted ensemble imports
  - grid_search/__init__.py — `from level_6` for re-exported grid helpers
  - grid_search/dataset_variant_executor.py — `from level_0`, `level_1`, `level_6`; typing imports sorted
  - grid_search/hyperparameter_base.py — `from level_0`, `level_6`; import order (itertools before typing)
  - grid_search/variant_result_builders.py — `from level_0`, `level_6`; typing sorted
  - level_7/README.md — dependencies + public API table
  - level_7/grid_search/README.md — dependencies
  - level_csiro/level_2/regression_ensemble_pipeline.py — fix wrong source package for `create_regression_ensemble_from_paths`

CALLERS TOUCHED (Phase 8):
  - scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_2/regression_ensemble_pipeline.py

VIOLATIONS REQUIRING HUMAN REVIEW:
  - None for level_7 layering after import normalization.

ITEMS FOR HUMAN JUDGMENT:
  - Full `import level_7` in this environment fails without optional deps (e.g. `torchvision` via level_1→level_3 import chain); same as precheck skip — use a venv with contest ML deps for runtime verification.

=== END AUDIT RESULT: level_7 ===
```

## Handoff for level_8 audit

- **level_7 internal rule:** All logic under `level_7` now uses **`from level_0` … `from level_6`** (no `layers.layer_0_core.level_K` in those modules).
- **Public API:** Unchanged; `level_8` and contests may keep `from layers.layer_0_core.level_7 import …` or align to `from level_7 import …` after `path_bootstrap.prepend_framework_paths()` per stack convention.
- **Bugfix surfaced here:** `create_regression_ensemble_from_paths` is a **level_8** export; CSIRO `regression_ensemble_pipeline.py` now imports it from `level_8`.
- **Relevant lower APIs:** level_6 grid-search surface (`GridSearchBase`, `auto_detect_grid_search_results`, `create_variant_specific_data`, tabular model classes, ensembling classes) remains the main dependency for level_7 orchestration helpers.
