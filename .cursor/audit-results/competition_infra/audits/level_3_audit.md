---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_3
pass_number: 1
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
run_id: comp_infra_overhaul_2026-04-08
---

# Audit: level_3 (competition infra)

**level_path:** `scripts/layers/layer_1_competition/level_0_infra/level_3`  
**Inventory:** `competition_infra/inventories/INVENTORY_level_3.md`  
**Precheck:** `competition_infra/summaries/precheck_level_3_2026-04-08.md` (clean machine scan)

=== PRIOR: level_0 ===

Barrels under `layers.layer_1_competition.level_0_infra.level_0`; registry/artifact/path helpers; `register_model_id_map`; `verify_export_output(..., export_dir=...)`.

=== PRIOR: level_1 ===

Contest CLI/loaders/export/features/grid_search/paths/pipelines/registry barrels; `ContestGridSearchBase`, `build_grid_search_context`, `create_feature_extraction_model` on infra `level_1` public API.

=== PRIOR: level_2 ===

`FeatureExtractionHelper` and related feature-extraction helpers; audit reported no edits that break `level_3` consumers.

---

## USER_REQUEST (honored)

- Fix inventory FLAGS: README drift vs code; `create_trainer` documented on `level_3` but owned by `level_4`; align barrels per `python-import-surfaces.mdc`.
- Persist this audit under `competition_infra/audits/level_3_audit.md`.

## Phase 1 — Functions & Classes

`FeatureExtractionTrainer` remains a single-responsibility two-stage trainer; no API or signature churn.

**Changes applied**

- `level_3/__init__.py` :: module docstring :: KISS :: removed stale “trainer factory and contest grid search” wording; tier 3 only aggregates `FeatureExtractionTrainer`.
- `level_3/trainer/__init__.py` :: module docstring :: accuracy :: removed incorrect `level_2` re-export claim; points only at `FeatureExtractionTrainer`.

PHASE 1 COMPLETE

## Phase 2 — Files

No splits/merges; `feature_extraction.py` stays within the `trainer` concept package.

PHASE 2 COMPLETE

## Phase 3 — Packages & Sub-packages

Structure already matches “concept, not type”: `trainer/` owns trainer implementation; no root-level orphan `.py` files besides `__init__.py`.

PHASE 3 COMPLETE

## Phase 4 — Legacy & Compatibility Purge

No deprecation shims, aliases, or compatibility branches found.

PHASE 4 COMPLETE

## Phase 5 — Full Level Review

- **Public API:** `level_3` barrel exports only `FeatureExtractionTrainer` (via `trainer.__all__`).
- **No infra-tier upward imports** from `level_3` modules to `level_4+`.
- **Human note:** `level_4/trainer/factory.py` imports `FeatureExtractionTrainer` from the **`level_3` barrel** (correct surface); `create_trainer` stays in `level_4`.

PHASE 5 COMPLETE

## Phase 6 — README & Documentation

| Path | Change |
|------|--------|
| `level_3/README.md` | README updated :: purpose/contents/API match code; `create_trainer` → `level_4`; grid search → `level_1`; examples corrected |
| `level_3/trainer/README.md` | README updated :: documents `feature_extraction.py` only; factory pointer to `level_4` |

PHASE 6 COMPLETE

## Phase 7 — Cross-Level Audit (competition_infra, tier K = 3)

### Precheck reconciliation

Machine precheck: no INFRA_TIER_UPWARD / DEEP_PATH / RELATIVE_IN_LOGIC / PARSE_ERROR entries; manual pass added consumer fixes below.

### 7a-contest — Import surfaces

- `level_4/trainer/factory.py` :: `from layers…level_0_infra.level_3.trainer import FeatureExtractionTrainer` → `from layers…level_0_infra.level_3 import FeatureExtractionTrainer` :: **INFRA_DEEP_PATH resolved** :: symbol on `level_3` `__all__` per `python-import-surfaces.mdc`.
- `level_1_impl/level_csiro/level_4/feature_extraction.py` :: `create_trainer` import `level_3` → `level_4` :: **resolved** :: factory lives in infra `level_4`.
- `level_4/fold_orchestration/single_fold.py` :: same `create_trainer` barrel fix :: **resolved** :: relies on `level_4/__init__.py` importing `trainer` before `fold_orchestration`.
- `level_1_impl/level_csiro/level_4/grid_search_context.py` :: `build_grid_search_context` `level_3` → `level_1` :: **resolved** :: grid search package is infra `level_1`.
- `level_1_impl/level_csiro/level_0/csiro_grid_search_base.py` :: `ContestGridSearchBase` `level_3` → `level_1` :: **resolved**.

### 7b–7d

No DRY/SOLID flags beyond correcting import entrypoints (symbols were already correct at their owning tiers).

PHASE 7 COMPLETE

## Phase 8 — Caller verification

CALLERS UPDATED:

- `scripts/layers/layer_1_competition/level_0_infra/level_4/trainer/factory.py` — barrel import for `FeatureExtractionTrainer`
- `scripts/layers/layer_1_competition/level_0_infra/level_4/fold_orchestration/single_fold.py` — `create_trainer` from infra `level_4`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_4/feature_extraction.py` — `create_trainer` from infra `level_4`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_4/grid_search_context.py` — `build_grid_search_context` from infra `level_1`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_0/csiro_grid_search_base.py` — `ContestGridSearchBase` from infra `level_1`

PHASE 8 COMPLETE

---

=== AUDIT RESULT: level_3 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):

- `FeatureExtractionTrainer` — two-stage trainer (feature extraction + regression head; optional `save_regression_model` on train)

CONSOLIDATED CHANGE LOG:

- Phase 1: 2 docstring corrections (`level_3` root, `trainer/__init__.py`)
- Phase 2: 0
- Phase 3: 0
- Phase 4: 0
- Phase 5: 0 code edits (review only)
- Phase 6: 2 READMEs rewritten for `level_3` tree; `level_4/fold_orchestration/README.md` dependency rows corrected; `level_1/grid_search/README.md` example corrected (grid search owns `level_1`, not `level_3`)
- Phase 7: 5 import-surface fixes (1 infra→infra barrel, 4 callers)
- Phase 8: 5 caller/module files touched (listed above)

Itemized:

- `level_0_infra/level_3/__init__.py` — docstring
- `level_0_infra/level_3/trainer/__init__.py` — docstring
- `level_0_infra/level_3/README.md` — align with code and cross-tier pointers
- `level_0_infra/level_3/trainer/README.md` — align with code
- `level_0_infra/level_4/trainer/factory.py` — `FeatureExtractionTrainer` from `level_3` barrel
- `level_0_infra/level_4/fold_orchestration/single_fold.py` — `create_trainer` from `level_4`
- `level_0_infra/level_4/fold_orchestration/README.md` — dependencies
- `level_0_infra/level_1/grid_search/README.md` — usage example no longer claimed grid-search re-exports from `level_3`
- `level_1_impl/level_csiro/level_4/feature_extraction.py` — `create_trainer` import
- `level_1_impl/level_csiro/level_4/grid_search_context.py` — `build_grid_search_context` import
- `level_1_impl/level_csiro/level_0/csiro_grid_search_base.py` — `ContestGridSearchBase` import

CALLERS TOUCHED (Phase 8):

- `scripts/layers/layer_1_competition/level_0_infra/level_4/trainer/factory.py`
- `scripts/layers/layer_1_competition/level_0_infra/level_4/fold_orchestration/single_fold.py`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_4/feature_extraction.py`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_4/grid_search_context.py`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_0/csiro_grid_search_base.py`

VIOLATIONS REQUIRING HUMAN REVIEW:

- None blocking.

ITEMS FOR HUMAN JUDGMENT:

- **Import-order churn:** CSIRO modules now pull grid-search symbols from infra `level_1`; if a future policy splits “heavy” contest deps, revisit whether CSIRO `level_0` should depend on infra `level_1` for base classes only (already the case after this fix).
- **Runtime verification:** Full `layers.layer_1_competition` import was not executed in this environment (torch/core import failure in sample `python -c`); recommend a smoke import on a machine with project deps installed.

=== END AUDIT RESULT: level_3 ===
