---
generated: 2026-04-08
audit_scope: general
level_name: level_5
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
---

# Audit: level_5

## Precheck reconciliation

`precheck_level_5_2026-04-08.md` reports **skipped_machine_script** (`ModuleNotFoundError: torchvision`). No machine violation list to reconcile in Phase 7.

---

## Phase 1 — Functions & classes

Reviewed against inventory: responsibilities are mostly cohesive. Large modules (`stacking_ensemble`, `operations`, `results_persistence`, `model_io`, `base_model_trainer`, `result_analysis`) remain single-concept but **file-size** candidates for a future split pass; no renames or extractions applied this pass to limit blast radius.

**Change log:** *(no structural SRP splits this pass)*

---

## Phase 2 — Files

No file renames or merges. **Line-count flags** from inventory (>300 LOC in several modules) noted for optional follow-up decomposition.

---

## Phase 3 — Packages

Structure is concept-based (batch_loading, datasets, grid_search, etc.); no catch-all `utils`. Root `level_5` has no stray `.py` files besides `__init__.py`.

---

## Phase 4 — Legacy & compatibility

**Finding:** Inventory noted `compat` in `model_io.py` — verified as docstring wording (“pickle-compatible”), not compatibility shims.

**Result:** No legacy deprecation/shim code removed.

---

## Phase 5 — Full level review

- **Applied:** Import-surface normalization and `__all__` hygiene (see Phase 7 / change log).
- **Circular / cohesion:** No same-level `level_5` imports in logic modules per inventory.
- **Human review:** Splitting oversized modules would touch many call sites; defer unless a benchmark or maintenance need appears.

---

## Phase 6 — README & documentation

| Path | Action |
|------|--------|
| `level_5/README.md` | **Updated** — removed nonexistent `metrics` subpackage; aligned Public API with composed `__all__`; fixed dependencies; runnable example without false symbols (`calculate_metrics` from root). |
| `level_5/metadata/README.md` | **Updated** — documented `scores.py`, `find_project_input_root`, import order in example. |

Subpackage READMEs elsewhere unchanged where still accurate.

---

## Phase 7 — Cross-level audit (general, N = 5)

### 7a — Import enforcement

**Applied fixes:** All logic modules under `level_5` used `from layers.layer_0_core.level_K import …` (filesystem path form). Per `python-import-surfaces.mdc`, general-stack logic must use **`from level_K import …`** after `path_bootstrap`. **Rewrote 24 modules** to public `level_0`…`level_4` imports, with alphabetical symbol order where touched.

**`metadata/paths.py`:** Removed **`__all__` from a leaf module** (violates `init-exports.mdc`). Public contract remains `metadata/__init__.py`.

**Violation log (pre-fix):**

- `level_5/**/*.py` (logic) :: `from layers.layer_0_core.level_K import …` :: **DEEP_PATH / wrong surface** :: use `from level_K import …` :: matches documented general-stack bootstrap.

**Post-fix:** No remaining `layers.layer_0_core.level_` imports under `level_5/`.

### 7b–7d

No new DRY/SOLID/KISS flags beyond existing “large file” notes; lower-level APIs are used rather than reimplemented.

---

## Phase 8 — Callers

No public symbol renames or signature changes. **No caller files updated.** External imports such as `from layers.layer_0_core.level_5 import …` remain valid (package location unchanged).

---

## Consolidated change log

1. **Import surface (all listed logic `.py` under `level_5`):** `layers.layer_0_core.level_K` → `level_K` per policy; import lists alphabetized where edited.
2. **`metadata/paths.py`:** removed leaf `__all__`.
3. **`level_5/README.md`**, **`level_5/metadata/README.md`:** accuracy pass.

---

```
=== AUDIT RESULT: level_5 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):
  From composed root __all__ (unchanged names): load_csv_batch, load_image_batch; JSONConfigLoader, create_json_model_registry, BaseTabularModel, SparseTabularDataset; load_and_validate_test_data, prepare_test_dataframe_with_dummy_targets, get_dataset_cache_dir, save_dataset_splits, load_dataset_splits, apply_train_val_split, get_max_augmentation_variant, get_dataset_variant_grid; apply_weighted_combination, combine_with_fallback, StackingEnsemble; ExportPipeline, find_trained_model_path, export_from_training_dir, copy_model_checkpoint, write_metadata_file; merge_json_from_input_and_working, merge_list_by_key_add_only, merge_list_by_key_working_replaces, save_submission_csv; grid_search exports (load/save results & checkpoint, raw results, extract/analyze/focused grid, cleanup, variant helpers); find_project_input_root, find_metadata_dir, get_writable_metadata_dir, load_combo_metadata, extract_scores_from_json, resolve_best_fold_and_score; save_model_raw, save_model, load_model_raw, load_model, save_regression_model; BaseModelTrainer, VisionTrainer.

CONSOLIDATED CHANGE LOG:
  Phase 1: 0 applied splits (notes only)
  Phase 2: 0
  Phase 3: 0
  Phase 4: 0 removals
  Phase 5: holistic pass; dependency fixes via Phase 7
  Phase 6: 2 READMEs updated
  Phase 7: import violations corrected (general-stack surface + leaf __all__)
  Phase 8: skipped — no API renames
  - Logic imports: layers.layer_0_core.level_* → level_* (24 files)
  - metadata/paths.py: removed __all__
  - level_5/README.md, metadata/README.md: documentation alignment

CALLERS TOUCHED (Phase 8):
  (none)

VIOLATIONS REQUIRING HUMAN REVIEW:
  - Optional decomposition of modules >300 LOC (stacking_ensemble, export/operations, grid_search/results_persistence, model_io/model_io, training/base_model_trainer, grid_search/result_analysis).

ITEMS FOR HUMAN JUDGMENT:
  - Environment without torchvision cannot import full level_1 → full level_5 barrel (pre-existing optional-dep graph).

=== END AUDIT RESULT: level_5 ===
```

---

## PRIOR: level_5 (handoff to level_6+)

**level_5** exposes the **composed root `__all__`** above: batch and image loading; JSON/tabular data structures; dataset test/split/variant helpers; ensembling (weighted + stacking); export pipeline + filesystem ops; JSON merge + submission CSV; full grid-search toolkit; metadata path + score helpers; model save/load; `BaseModelTrainer` and `VisionTrainer`.

**Imports from lower general tiers:** `level_0`–`level_4` only, via **`from level_K import …`** in logic files.

**Notable constraint:** Importing `level_5` eagerly loads subpackages (e.g. `batch_loading` → `level_1`), which may require optional deps such as **torchvision** in minimal environments.
