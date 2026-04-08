---
generated: 2026-04-08
audit_scope: general
level_name: level_4
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
---

# Audit: level_4

## Pre-flight

- **Inventory:** `INVENTORY_level_4.md` — verified complete (`INVENTORY: level_4`).
- **Precheck:** `precheck_level_4_2026-04-08.md` — machine script skipped (`ModuleNotFoundError: torchvision`). Phase 7 has **no machine violation checklist** to reconcile; import audit performed manually against `python-import-surfaces.mdc` / `architecture.mdc`.

## Phase 1 — Functions & Classes

- Reviewed inventory-listed symbols: responsibilities are broadly coherent (dataloaders, ensemble meta-model, SigLIP helpers, typed file I/O, metric dispatch, vision factory, pipeline classes, progress tracker).
- **Doc / naming polish (applied):** `ensemble/meta_model_stacking.py` module note now points to `simple_average` from **level_2** without a filesystem-deep path string.
- **SigLIP adapter (applied):** `siglip_adapter.py` module and class docstrings reworded to describe a **FeatureExtractor-style contract** (avoids stale “compat” phrasing and clarifies intent).

**Change log**

- `meta_model_stacking.py` :: module docstring :: KISS :: remove misleading submodule path; reference public `level_2` API.
- `siglip_adapter.py` :: docstrings :: naming/clarity :: describe adapter contract without vague “compat” wording.

## Phase 2 — Files

- **Large modules (flagged, not split in this pass):** `create_dataloaders.py` (~320), `calculate_metrics.py` (~303), `evaluate_pipeline.py` (~358), `submission_averaging.py` (~574). Splitting would reduce SRP pressure but increases churn for higher levels; defer unless orchestrator requests decomposition pass.

**Change log**

- (none — no renames/splits applied)

## Phase 3 — Packages & Sub-packages

- No root-level stray `.py` files besides `__init__.py` (per inventory).
- **Root `__init__.py` docstring (applied):** removed incorrect “training” claim; listed actual concerns (dataloaders, features, ensemble, file I/O, metrics, models, pipelines, runtime).

**Change log**

- `level_4/__init__.py` → docstring only :: align with actual subpackages.

## Phase 4 — Legacy & Compatibility Purge

No deprecation shims, `OldName = NewName`, or commented legacy blocks found in audited sources.

## Phase 5 — Full Level Review

- **Imports:** All logic files now use **`from level_K import …`** (K \< 4), matching `level_3` and `python-import-surfaces.mdc` (after `path_bootstrap`).
- **Import groups:** Adjusted where needed (e.g. blank line before `level_*` block; alphabetical ordering within multi-import `from level_3` lists where touched).
- **Circular risk:** Unchanged; no new cross-level cycles introduced.
- **Human review:** Optional decomposition of oversize pipeline/dataloader/metrics modules; `threshold_optimization.py` depends on **scipy** (third-party) — acceptable for optimization helper.

**Dependency rule violations:** None found after normalization.

## Phase 6 — README & Documentation

**Change log**

- `level_4/README.md` :: README updated :: metrics row and Public API table aligned with `calculate_metrics` / `calculate_metric_by_name`; CSV/JSON rows include `load_csv_raw_if_exists`, `load_best_config_json`, `save_json_atomic`; **level_1** dependencies expanded (`get_metric`, `list_metrics`, `validate_config_section_exists`).

Sub-package READMEs (`dataloaders`, `ensemble`, `features`, `file_io`, `metrics`, `models`, `pipeline`, `runtime`) reviewed: `metrics/README.md` already matches current behavior; no edits required there.

## Phase 7 — Cross-Level Audit

**7a — Import rule enforcement (general, N = 4)**

- **VALID:** stdlib / third-party only, or `from level_0` … `from level_3` in logic files.
- **VALID:** `__init__.py` relative aggregation only.
- **Resolved (was non-canonical):** `from layers.layer_0_core.level_K import …` in logic files → rewritten to **`from level_K import …`** (surface form required for general stack after bootstrap).

No `WRONG_LEVEL`, `DEEP_PATH` (into `level_K.subpkg`), `IMPORT_STYLE` (relative in logic), or `UPWARD VIOLATION` remains in `level_4` logic.

**7b–7d:** No duplicate re-implementations identified that clearly belong in lower levels beyond normal composition; `calculate_metrics` correctly dispatches to `level_1` registry + `level_3` metric bundles.

**Violation log**

- (none remaining)

## Phase 8 — Caller verification

**No public API renames, moves, or signature changes.** Edits are confined to **internal import strings** and documentation inside `level_4`.

**CALLERS UPDATED:**

- (none — internal-only import path form)

---

## Result block (orchestrator)

```
=== AUDIT RESULT: level_4 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):
  Composed barrel from subpackages — same contract as before: dataloaders (`create_dataloaders`, `create_test_dataloader`), ensemble (`stacking_ensemble_with_validation`), features (`compute_siglip_embeddings`, `SigLIPFeatureExtractorAdapter`), full `file_io` surface (CSV/image/JSON/memmap/pickle/YAML helpers and constants), metrics (`calculate_metrics`, `calculate_metric_by_name`, `create_weighted_r2_calculator`), models (`create_vision_model`), pipeline (`EvaluatePipeline`, `SubmissionAveragingWorkflow`, `optimize_threshold`), runtime (`ProgressTracker`). See `level_4/__init__.__all__` for the authoritative flat list.

CONSOLIDATED CHANGE LOG:
  Phase 1: 2 doc/docstring touch-ups (stacking note, SigLIP adapter wording)
  Phase 2: 0 (large-file split deferred)
  Phase 3: 1 root __init__ docstring fix
  Phase 4: 0
  Phase 5: normalization of all cross-level imports to `from level_K`
  Phase 6: 1 README update (level_4 root)
  Phase 7: import surface violations corrected (layers.layer_0_core.level_K → level_K); precheck machine list N/A
  Phase 8: skipped — no API/signature changes
  Files touched: level_4/__init__.py; dataloaders/create_dataloaders.py; ensemble/meta_model_stacking.py; features/compute_siglip_embeddings.py; features/siglip_adapter.py; file_io/{csv,json,images,memmap,pickle,yaml}.py; metrics/{calculate_metrics,weighted_r2}.py; models/vision_model_factory.py; pipeline/{evaluate_pipeline,submission_averaging,threshold_optimization}.py; runtime/progress_tracker.py; README.md

CALLERS TOUCHED (Phase 8):
  (none)

VIOLATIONS REQUIRING HUMAN REVIEW:
  - Environment: full import smoke test blocked without `torchvision` (matches precheck skip).
  - Optional: split `submission_averaging.py` / `evaluate_pipeline.py` / `create_dataloaders.py` / `calculate_metrics.py` if maintainability priority increases.

ITEMS FOR HUMAN JUDGMENT:
  - Whether to invest in splitting >300-line modules vs keeping stable API surface.

=== END AUDIT RESULT: level_4 ===
```
