---
generated: 2026-04-08
audit_scope: general
level_name: level_3
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
inventory: .cursor/audit-results/general/inventories/INVENTORY_level_3.md
precheck_report_path: .cursor/audit-results/general/summaries/precheck_level_3_2026-04-08.md
---

# Audit: level_3

## Phase 1 — Functions & classes

Reviewed against inventory; no SRP splits required for this pass. Minor hygiene: removed unused `Tuple` import in `handle_stacking_results.py`.

**Change log**

- `ensemble_strategies/handle_stacking_results.py` :: (import) → removed unused `Tuple` :: YAGNI :: typing cleanup

---

## Phase 2 — Files

No file renames or splits. `factory.py` name overlap across `dataloader/` and `transforms/` remains acceptable (different packages).

---

## Phase 3 — Packages

No structural moves. Root `level_3` has no orphan root-level `.py` files (only `__init__.py` + `README.md`). Added missing `ensemble_strategies/README.md`.

**Change log**

- `[new] ensemble_strategies/README.md` :: document Purpose/Contents/Public API/Dependencies/Usage per package standard

---

## Phase 4 — Legacy & compatibility

No deprecation shims, aliased compatibility names, or commented legacy blocks found.

---

## Phase 5 — Full level review

- **Import layering:** All logic files now depend only on `level_0`–`level_2` via public `from level_N import …` surfaces (Phase 7).
- **Circular imports:** No changes that introduce same-level logic imports.
- **Human review:** `metrics/__init__.py` import-time registration side effect is intentional and documented in-module.

---

## Phase 6 — README & documentation

**Change log**

- `level_3/README.md` :: README updated :: corrected import policy (path_bootstrap + `from level_0|1|2`; `__init__.py` relatives only); documented `ensemble_strategies` in Contents and key exports
- `level_3/ensemble_strategies/README.md` :: README created :: full section template for the previously undocumented package

Sub-package READMEs under `dataloader`, `ensemble`, `features`, `metrics`, `runtime`, `training`, `transforms`, `workflows` were not rewritten; they remain accurate for behavior.

---

## Phase 7 — Cross-level audit

**Precheck:** Machine script unavailable (`ModuleNotFoundError: torchvision`); no automated violation list to reconcile. Manual scan applied.

**7a — Import enforcement (general `level_3`, N = 3)**

| Action | Detail |
|--------|--------|
| Fixed | Replaced **`from layers.layer_0_core.level_K import …`** with **`from level_K import …`** in all logic files (22 modules) — aligns with `python-import-surfaces.mdc` and auditor DEEP_PATH/long-path avoidance for the general stack. |
| Fixed | Removed unused **`is_kaggle`** import from `ensemble_strategies/pipeline_result_handler.py`. |
| Valid | `__init__.py` files: relative imports only — unchanged. |

**Violation log (resolved in-repo)**

- `[multiple]` :: `from layers.layer_0_core.level_* import …` :: import surface / style :: rewrite to `from level_*` :: public API form after path bootstrap

**7b–7d**

No duplicate implementations flagged that clearly belong in lower levels beyond existing intentional composition.

---

## Phase 8 — Caller verification

No changes to exported symbol names or `level_3` package paths consumed by other trees. Internal import spelling change (`layers.layer_0_core.level_*` → `level_*`) is confined to files under `level_3`.

**CALLERS UPDATED:** none (skipped — no public API renames or moves)

---

## Consolidated edits (files touched)

- `dataloader/factory.py` — imports
- `dataloader/transforms.py` — imports
- `ensemble/blending_ensemble.py` — imports
- `ensemble/create_meta_model.py` — imports
- `ensemble/per_target_weighted.py` — imports
- `ensemble_strategies/handle_regression_ensemble_result.py` — imports
- `ensemble_strategies/handle_stacking_results.py` — imports, unused `Tuple`
- `ensemble_strategies/pipeline_result_handler.py` — imports, drop unused `is_kaggle`
- `ensemble_strategies/README.md` — new
- `features/extract_all_features.py` — imports
- `features/handcrafted_feature_extraction.py` — imports
- `features/siglip_extractor.py` — imports
- `features/supervised_embedding_engine.py` — imports
- `metrics/classification.py` — imports
- `metrics/regression.py` — imports
- `runtime/path_validation.py` — imports, blank line before first `def`
- `training/oom_retry.py` — imports
- `training/sklearn_models.py` — imports
- `training/timm_model.py` — imports
- `training/tta_predictor.py` — imports
- `transforms/factory.py` — imports
- `workflows/progress_formatter.py` — imports
- `workflows/train_test_pipeline.py` — imports
- `README.md` (level_3 root) — import policy + contents

---

## Items for human judgment

- Optional future split of `dataloader/factory.py` or `transforms/factory.py` if they grow past maintainability; current line counts are acceptable per inventory.
- Full `import level_3` smoke test requires optional deps (`torchvision`, etc.) in the runtime environment.

---

```
=== AUDIT RESULT: level_3 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):
  Union of sub-package __all__ per level_3/__init__.py: dataloader (create_train_dataloader, create_val_dataloader, build_transforms_for_dataloaders), ensemble_strategies (handle_regression_ensemble_result, handle_stacking_result, handle_hybrid_stacking_result, handle_ensemble_result), ensemble (blend_predictions, learn_blending_weights, create_meta_model, PerTargetWeightedEnsemble), features (extract_all_features, extract_handcrafted_features_for_ids, extract_handcrafted_parallel, stream_features, SigLIPExtractor, SupervisedEmbeddingEngine), metrics (all classification/regression functions and *Metric classes listed in metrics/__init__.__all__), runtime (validate_file_exists, validate_path_is_file, validate_image_path, validate_image_paths_in_dataframe), training (handle_oom_error_with_retry, HistGradientBoostingRegressorModel, GradientBoostingRegressorModel, CatBoostRegressorModel, LGBMRegressorModel, XGBoostRegressorModel, RidgeRegressorModel, create_regression_model, TimmModel, TTAPredictor), workflows (ProgressFormatter, train_test_pipeline), plus build_train_transform, build_val_transform, build_tta_transforms from transforms.

CONSOLIDATED CHANGE LOG:
  Phase 1: 1 (unused import removal)
  Phase 2: 0
  Phase 3: 1 (new ensemble_strategies README)
  Phase 4: 0
  Phase 5: narrative only
  Phase 6: 2 (root README update + ensemble_strategies README)
  Phase 7: import surface normalization across 22 logic modules + unused import removals
  Phase 8: skipped — no API changes

CALLERS TOUCHED (Phase 8):
  (none)

VIOLATIONS REQUIRING HUMAN REVIEW:
  (none after applied fixes)

ITEMS FOR HUMAN JUDGMENT:
  - Optional future splits of large factory modules; env with torchvision needed for full import smoke test.

=== END AUDIT RESULT: level_3 ===
```

### PRIOR: level_3 (handoff)

Barrel: `level_3.__init__` composes sub-packages (`dataloader`, `ensemble_strategies`, `ensemble`, `features`, `metrics`, `runtime`, `training`, `transforms`, `workflows`) and re-exports their `__all__` plus `build_train_transform`, `build_val_transform`, `build_tta_transforms`.

**Imports in logic files:** `from level_0`, `from level_1`, `from level_2` only (alphabetized names within blocks where edited). **Init-only:** relative `from .` aggregation.

**Notable APIs:** Same as pre-audit inventory; `log_pipeline_completion` consumed from `level_2` in ensemble_strategies handlers; metrics package still auto-registers on import.
