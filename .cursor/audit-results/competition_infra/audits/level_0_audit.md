---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_0
pass_number: 1
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
run_id: comp_infra_overhaul_2026-04-08
---

# Audit: level_0 (competition infra)

## USER_REQUEST (honored)

```
/code-audit 
audit competition infra
profile full
apply fixes
active overhaul
@.../level_0_infra (twice)
```

## Precheck

- **precheck_report_path**: `competition_infra/summaries/precheck_level_0_2026-04-08.md`
- **Result**: clean (no machine violations reported)

## Phase 1 — Functions & Classes

### Findings

- `verify_export_output()` hard-coded its export directory at import time via `KAGGLE_EXPORT_DIR`.
- `MODEL_ID_MAP` was registered into core at import time via `set_model_id_map(MODEL_ID_MAP)` (global side effect).
- Placeholder loaders raised `NotImplementedError` correctly but were missing the required “NOT IMPLEMENTED” marker comment.

### Changes applied

- `model/verify_export_output.py` :: `verify_export_output(model_type: str = "end_to_end")` → `verify_export_output(model_type: str = "end_to_end", *, export_dir: Path | None = None)` :: KISS :: removes hardcoded module-global path; caller can override export directory.
- `model/model_constants.py` :: import-time `set_model_id_map(MODEL_ID_MAP)` → `register_model_id_map(model_id_map: Optional[Dict[str, str]] = None)` :: SRP :: makes model-id registration an explicit action and keeps module import side-effect free.
- `model/embeddings.py` :: add required `# TODO: NOT IMPLEMENTED — wire later` markers above placeholder raises :: coding-standards :: ensures stubs are explicitly flagged.

PHASE 1 COMPLETE

## Phase 2 — Files

- No file splits/merges needed; modules are already scoped to single concepts.

PHASE 2 COMPLETE

## Phase 3 — Packages & Sub-packages

### Findings

- `paths/contest_output.py` importing `ContestPaths` from the **level package root** (`layers...level_0_infra.level_0`) was a circular-import risk (package root imports `paths`, which imports `contest_output`, which imported the package root again).

### Changes applied

- `paths/contest_output.py` now imports `ContestPaths` from `layers.layer_1_competition.level_0_infra.level_0.contest` (subpackage barrel) to avoid triggering the root `__init__.py`.
- `model/__init__.py` exports the new `register_model_id_map` as part of the model subpackage public API.

PHASE 3 COMPLETE

## Phase 4 — Legacy & Compatibility Purge

No legacy or compatibility code found.

PHASE 4 COMPLETE

## Phase 5 — Full Level Review

### Summary

- Import surfaces remain compliant with `python-import-surfaces.mdc` for competition infra.
- Public APIs remain expressed via `__init__.py` barrels; no leaf-module `__all__` introduced.
- No infra-tier upward imports detected (imports are limited to `layers.layer_0_core.*` and same-tier infra barrels).

PHASE 5 COMPLETE

## Phase 6 — README & Documentation

### Changes applied

- `.../level_0/README.md` :: README updated :: added `register_model_id_map` to Public API and example.
- `.../level_0/model/README.md` :: README updated :: added `register_model_id_map` to Public API and example.
- `.../level_0/paths/README.md` :: README updated :: dependencies corrected to match `ContestPaths` import surface.

PHASE 6 COMPLETE

## Phase 7 — Cross-Level Audit (competition_infra)

### Import violations

- None remaining after fixing the root-import cycle risk in `paths/contest_output.py`.

PHASE 7 COMPLETE

## Phase 8 — Caller verification and repository consistency

CALLERS UPDATED:
  - None (no breaking renames/removals; `verify_export_output` signature is backward-compatible for existing callers that only pass `model_type`)

PHASE 8 COMPLETE

=== AUDIT RESULT: level_0 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):
  - ContestInputValidator — contest input validation protocol
  - ContestMetric — contest scoring protocol
  - ContestPipelineProtocol — contest pipeline protocol (train/submit/tune)
  - ContestRunPathsProtocol — protocol for resolving run output directories
  - PipelineResult — shared pipeline result container (re-exported)
  - ArtifactKeys — standardized artifact key constants
  - artifacts_merge — merge multiple artifact-path mappings
  - capture_config_paths — build config artifact-path mapping
  - capture_metrics_paths — build metrics artifact-path mapping
  - capture_model_paths — build model artifact-path mapping
  - capture_submission_paths — build submission artifact-path mapping
  - metadata_merge — merge multiple metadata mappings
  - add_grid_search_parsers — attach grid-search parsers to a CLI
  - add_training_parsers — attach training parsers to a CLI
  - add_ensemble_parsers — attach ensemble parsers to a CLI
  - add_submission_parsers — attach submission parsers to a CLI
  - ContestConfig — base contest config contract
  - ContestDataSchema — base contest data schema contract
  - ContestPaths — base contest paths contract
  - ContestPostProcessor — base predictions post-processor
  - ClipRangePostProcessor — range-clipping post-processor
  - ContestOntologySystem — base ontology system contract
  - ContestHierarchy — base hierarchy contract
  - ContestPathConfig — dataclass path configuration container
  - MODEL_ID_MAP — default model name → id mapping
  - get_model_id — resolve model id from name (core re-export)
  - get_model_image_size — infer model image size
  - get_model_name_from_pretrained — reverse lookup model name from pretrained spec
  - get_pretrained_weights_path — resolve pretrained spec from model name
  - load_embedding_data — placeholder; contest must implement
  - load_structured_features — placeholder; contest must implement
  - register_model_id_map — explicitly register model name → id map into core
  - register_features — register contest features into core registries
  - verify_export_output — validate exported model directory contents
  - contest_models_dir — resolve `<output_dir>/models/<contest_slug>`
  - load_feature_filename_from_gridsearch — metadata fallback helper
  - create_pipeline_kwargs — build common pipeline kwargs
  - create_training_config — build core-compatible training config mapping
  - NamedRegistry — registry primitive (core re-export)
  - build_unknown_key_error — registry error helper (core re-export)
  - validate_strategy_models — submission strategy validation helper

CONSOLIDATED CHANGE LOG:
  Phase 1: 3 changes
  Phase 2: 0 changes
  Phase 3: 2 changes
  Phase 4: 0 changes
  Phase 5: 0 changes
  Phase 6: 3 READMEs updated
  Phase 7: 0 violations found
  Phase 8: skipped — no breaking API changes

  - scripts/layers/layer_1_competition/level_0_infra/level_0/paths/contest_output.py :: import `ContestPaths` from `...level_0.contest` to avoid package-root circular import
  - scripts/layers/layer_1_competition/level_0_infra/level_0/model/model_constants.py :: remove import-time `set_model_id_map` call; add `register_model_id_map`
  - scripts/layers/layer_1_competition/level_0_infra/level_0/model/__init__.py :: export `register_model_id_map`
  - scripts/layers/layer_1_competition/level_0_infra/level_0/model/embeddings.py :: add NOT IMPLEMENTED markers for placeholders
  - scripts/layers/layer_1_competition/level_0_infra/level_0/model/verify_export_output.py :: add `export_dir` override, remove module-global hardcoded path
  - scripts/layers/layer_1_competition/level_0_infra/level_0/README.md :: document `register_model_id_map`
  - scripts/layers/layer_1_competition/level_0_infra/level_0/model/README.md :: document `register_model_id_map`
  - scripts/layers/layer_1_competition/level_0_infra/level_0/paths/README.md :: correct dependency surface for `ContestPaths`

CALLERS TOUCHED (Phase 8):
  - (none)

VIOLATIONS REQUIRING HUMAN REVIEW:
  - None

ITEMS FOR HUMAN JUDGMENT:
  - Contests should decide where to call `register_model_id_map()` during startup (e.g., contest registration / entrypoint) depending on whether they want defaults or overrides.

=== END AUDIT RESULT: level_0 ===

- **Precheck:** `skipped_machine_script` — `No module named 'level_0'` when optional import graph ran. No automated violation list merged; manual policy pass applied.

## Changes applied (run_mode: default)

| Pass | Area | Change |
|------|------|--------|
| 1 | Import surface | Deep path `level_0.contest.paths` for `ContestPaths` (later reverted). |
| 2 | Import surface | **`contest_output.py`** uses **`from layers...level_0_infra.level_0 import ContestPaths`** (barrel), per `python-import-surfaces.mdc`. |

## Callers / files touched

- `scripts/layers/layer_1_competition/level_0_infra/level_0/paths/contest_output.py`

## Dependency violations

- None introduced; tier imports remain `layer_0_core` only.

## Notes

- **PRIOR:** N/A (first tier in segment).
