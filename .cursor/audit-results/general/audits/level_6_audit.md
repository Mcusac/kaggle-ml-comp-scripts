---
generated: 2026-04-08
audit_scope: general
level_name: level_6
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
---

# Audit: level_6

**Inventory:** `general/inventories/INVENTORY_level_6.md`  
**Precheck:** `precheck_level_6_2026-04-08.md` — **skipped_machine_script** (`torchvision` missing); Phase 7 had no machine violation list to reconcile.

**Note:** `general/audits/level_5_audit.md` was not present at orchestration time; cross-level policy applied: `level_6` may import `level_0`…`level_5` only. Inventory matched that.

---

## PHASE 1 — Functions & classes

Reviewed against inventory; structures are coherent (ensembling methods = thin `EnsemblingMethod` adapters, grid search split across base/results/handlers/variant modules, tabular trainers predictors MLP).

**Changes applied**

- `create_test_dataloader` (CSV streaming) → **`create_streaming_test_dataloader`** :: naming / SRP :: disambiguate from `level_4.create_test_dataloader` (DataFrame-based) and remove overloaded symbol on `level_6` public API.

**PHASE 1 COMPLETE**

---

## PHASE 2 — Files

**Changes applied**

- `prediction/create_test_dataloader.py` → **`prediction/streaming_test_dataloader.py`** :: filename matches streaming/CSV-specific factory.

**PHASE 2 COMPLETE**

---

## PHASE 3 — Packages

- No new sub-packages; `metadata/` remains a small two-file package (acceptable).
- Root `level_6` has no orphan `.py` besides `__init__.py`.

**PHASE 3 COMPLETE**

---

## PHASE 4 — Legacy & compatibility

No deprecation warnings, shims, or compat aliases found in audited sources.

**No legacy or compatibility code found.**

**PHASE 4 COMPLETE**

---

## PHASE 5 — Full level review

- **Dependency rule:** All logic imports lower tiers only (`level_0`…`level_5`); no `level_6` self-imports, no upward imports.
- **DRY:** Ensemble classes remain thin wrappers over `level_2` / `level_5` — acceptable.
- **Root `__init__.py`:** Still aggregates sub-packages only per `init-exports.mdc`.

**PHASE 5 COMPLETE**

---

## PHASE 6 — README & documentation

| Path | Action |
|------|--------|
| `level_6/README.md` | Updated — streaming loader name, vision section (registry only), metadata row + `find_combo_id_from_config`, removed stale `VisionTrainer` example import |
| `level_6/prediction/README.md` | Replaced — `create_streaming_test_dataloader`, module rename |
| `level_6/metadata/README.md` | **Created** — Purpose, Contents, Public API, Dependencies, Usage |
| `layers/.../level_0_infra/level_2/README.md` | Updated dependency bullet: `create_streaming_test_dataloader` |
| `layers/.../level_0_infra/level_2/feature_extraction/README.md` | Same |

**PHASE 6 COMPLETE**

---

## PHASE 7 — Cross-level audit (general, N = 6)

Precheck produced **no** automated violations (script skipped).

**7a — Import enforcement**

| Resolution | Detail |
|------------|--------|
| **Fixed (was policy drift)** | Logic and `grid_search/__init__.py` used `from layers.layer_0_core.level_K import …` — treated as non-canonical for the general stack vs `python-import-surfaces.mdc` / Phase 7a “public API form”. Rewrote to **`from level_K import …`** throughout `level_6` Python sources. |

- **VALID:** All `from level_K` with K < 6; `PredictPipeline` correctly uses `level_4.create_test_dataloader` for vision (DataFrame path from kwargs).
- **No** `WRONG_LEVEL`, `UPWARD VIOLATION`, or same-level `level_6` logic imports observed after edits.

**7b–7d:** No new cross-level DRY/SOLID issues introduced; grid barrel still re-exports `level_5` grid helpers intentionally.

**PHASE 7 COMPLETE**

---

## PHASE 8 — Callers

**API rename:** `create_test_dataloader` → `create_streaming_test_dataloader` on `level_6` public surface.

**CALLERS UPDATED**

- `scripts/layers/layer_1_competition/level_0_infra/level_2/feature_extraction/test_extractor.py`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_2/regression_ensemble_pipeline.py`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_1/test_pipeline.py`
- `scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_0/stacking_utils.py`

**PHASE 8 COMPLETE**

---

## Verification note

Local `python -c` import of full `level_6` after `path_bootstrap` may still fail if **`torchvision`** is not installed (failure observed in `level_1` import chain). This matches the precheck skip reason and is environmental, not specific to `level_6` edits.

---

=== AUDIT RESULT: level_6 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):

- From `ensembling`: `SimpleAverageEnsemble`, `WeightedAverageEnsemble`, `RankedAverageEnsemble`, `PercentileAverageEnsemble`, `TargetSpecificEnsemble` — averaging-based `EnsemblingMethod` implementations.
- From `grid_search`: `GridSearchBase`, focused/grid helpers, result handlers, variant grid/cleanup symbols — same barrel as before (re-exports `level_5` grid persistence/helpers plus local implementations).
- From `metadata`: `find_combo_id_from_config` — combo id lookup from config/metadata.
- From `prediction`: `PredictPipeline` — vision/tabular prediction pipeline; `create_streaming_test_dataloader` — CSV + streaming test loader (not `level_4` DataFrame factory).
- From `tabular`: `TabularTrainer`, `TabularPredictor`, `MLPModel`.
- From `tabular_models`: `LogisticRegressionModel`, `RidgeModel`, `XGBoostModel`, `LightGBMModel`.
- From `vision`: `get_vision_model_config`, `list_vision_models`.

CONSOLIDATED CHANGE LOG:

- Phase 1: Renamed public streaming factory to `create_streaming_test_dataloader` (clarity vs `level_4`).
- Phase 2: Renamed module to `streaming_test_dataloader.py`.
- Phase 3: None.
- Phase 4: None.
- Phase 5: None beyond import/API consistency.
- Phase 6: Root README, prediction README, new metadata README; infra level_2 README dependency lines.
- Phase 7: Normalized all `level_6` logic/barrel imports from `layers.layer_0_core.level_K` → `from level_K`.
- Phase 8: Four competition/infra Python callers updated for new symbol name; infra READMEs aligned.

CALLERS TOUCHED (Phase 8):

- `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra/level_2/feature_extraction/test_extractor.py`
- `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_2/regression_ensemble_pipeline.py`
- `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_1/test_pipeline.py`
- `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_csiro/level_0/stacking_utils.py`

VIOLATIONS REQUIRING HUMAN REVIEW:

- None for layering after import normalization.

ITEMS FOR HUMAN JUDGMENT:

- **`grid_search/__init__.py`** continues to re-export many **`level_5`** symbols at **`level_6`** — intentional convenience barrel; acceptable if product owners want a single import site for grid tooling vs tightening surface area.

=== END AUDIT RESULT: level_6 ===

---

## PRIOR: level_6 (handoff for level_7+)

- **Public API:** Re-export hub at `level_6/__init__.py` composing `ensembling`, `grid_search`, `metadata`, `prediction`, `tabular`, `tabular_models`, `vision` `__all__` lists.
- **Import rule for consumers:** After `path_bootstrap`, use **`from level_6 import …`** for this tier; do not import `level_6` leaf modules directly for symbols listed on `__init__.py` / `__all__`.
- **Breaking change this pass:** Replace **`from level_6 import create_test_dataloader`** with **`create_streaming_test_dataloader`** anywhere outside the four files already patched (grep `package_dumps`/notebooks if used).
- **Depends on:** `level_0`…`level_5` only; **`PredictPipeline`** uses **`level_4.create_test_dataloader`** for in-memory vision test data (distinct from streaming factory).
