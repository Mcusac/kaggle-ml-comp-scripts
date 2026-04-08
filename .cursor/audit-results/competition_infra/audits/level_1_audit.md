---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_1
pass_number: 1
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
run_id: comp_infra_overhaul_2026-04-08
---

# Audit: level_1 (competition infra)

**level_path:** `scripts/layers/layer_1_competition/level_0_infra/level_1`  
**Inventory:** `competition_infra/inventories/INVENTORY_level_1.md`  
**Precheck:** `competition_infra/summaries/precheck_level_1_2026-04-08.md` (clean for INFRA_TIER_UPWARD, DEEP_PATH, RELATIVE_IN_LOGIC, PARSE_ERROR)  
**Prior:** `competition_infra/audits/level_0_audit.md` — barrels under `level_0`; `register_model_id_map`; `ContestPaths`; `verify_export_output(..., export_dir=...)`.

## Phase 1 — Functions & Classes

### Findings

- Missing `contest/pipeline_shells.py` broke imports and duplicated ownership: shell types already live in `layers.layer_0_core.level_1.pipelines`.
- `contest/data_loading.py` imported the `level_1` package root while `level_1/__init__.py` imports `contest`, creating unnecessary circular coupling.

### Changes applied

- `contest/__init__.py` — import `BasePipeline`, `ValidateFirstRunner`, `ValidateFirstPipelineResultShell`, `TwoStageValidateFirstPipelineResultShell` from `layers.layer_0_core.level_1.pipelines` :: DRY / KISS :: single source of truth in core; fixes missing module.
- `contest/data_loading.py` — replace `from …level_1 import (ContestRegistry, get_contest, load_training_csv, split_train_val)` with explicit `contest.csv_io`, `contest.splits`, and `registry` submodule imports :: SRP / dependency :: breaks `level_1` ↔ `contest` package init cycle risk.

PHASE 1 COMPLETE

## Phase 2 — Files

- No renames or splits; `path_utils.py` naming remains a **naming** nit (inventory flag); renaming would be churn without dependency wins.

PHASE 2 COMPLETE

## Phase 3 — Packages & Sub-packages

- No structural moves; pipeline shells correctly stay aggregated at `contest` public API for callers such as `…level_1.contest` / `…level_1` imports.

PHASE 3 COMPLETE

## Phase 4 — Legacy & Compatibility Purge

- `export/export_model_pipeline.py` — removed the word `legacy` from the Scenario 4 comment :: coding-standards :: avoid stale/compatibility wording.

PHASE 4 COMPLETE

## Phase 5 — Full Level Review

### Dependency rule (infra tier K = 1)

- No **INFRA_TIER_UPWARD** (no imports from `level_0_infra/level_2+` incorrectly classified here).
- General-stack imports from `layers.layer_0_core` remain downward-only relative to those packages.

### Consolidated deltas (Phases 1–5)

- Shell types: local missing module → core `level_1.pipelines`.
- Data loading: package-root import → submodules.
- Paths: `is_kaggle_input` via `level_0` barrel; `contest_models_dir` via `level_0` barrel in `paths/models.py`.

### Items for human review

- `grid_search/__init__.py` re-exports `load_best_config_json` from `layers.layer_0_core.level_4` (convenience facade); acceptable but slightly blurs “grid_search only” narrative.
- `ContestGridSearchBase.__init__` uses a nested `_SimplePaths` class (inventory note); low priority unless testing/mocking suffers.

PHASE 5 COMPLETE

## Phase 6 — README & Documentation

| Path | Change |
|------|--------|
| `level_1/README.md` | README updated :: aligned with actual subpackages and dependencies |
| `level_1/contest/README.md` | README created |
| `level_1/paths/README.md` | README created |
| `level_1/pipelines/README.md` | README created |
| `level_1/registry/README.md` | README created |
| `level_1/handlers/commands/README.md` | README created |
| `level_1/export/README.md` | README updated :: removed stale `export_handlers` narrative; documented export cycle |

PHASE 6 COMPLETE

## Phase 7 — Cross-Level Audit (competition_infra, tier K = 1)

### Precheck reconciliation

- Machine precheck listed no violations; manual pass confirmed **7a-contest** alignment after edits.

### 7a-contest — Import surfaces

- `paths/models.py` :: `from layers…level_0.paths import contest_models_dir` → `from layers…level_0 import contest_models_dir` :: **resolved** :: symbol on `level_0` root `__all__` per `python-import-surfaces.mdc`.
- `paths/__init__.py` :: `from layers…level_0.runtime.platform_detection import is_kaggle_input` → `from layers…level_0 import is_kaggle_input` :: **resolved** :: barrel preference.
- `contest/data_loading.py` :: submodule imports for `load_training_csv` / `split_train_val` / registry :: **VALID (cycle break)** :: same spirit as `architecture.mdc` circular-import exception; importing `contest` package root from within `contest` while it initializes is avoided.
- `export/export_model_pipeline.py` :: `from …level_1.export.source_handlers import …` :: **kept** :: importing via `export` package `__init__` would cycle; documented in `export/README.md`.

### 7b–7d — Cross-level DRY / SOLID / KISS

- Pipeline shells: **removed duplicate ownership** by binding contest exports to `layers.layer_0_core.level_1.pipelines`.
- No additional flags: level_1 continues to consume `level_0` public types (`ContestPaths`, `PipelineResult`, `create_pipeline_kwargs`, etc.) consistent with **level_0** audit.

PHASE 7 COMPLETE

## Phase 8 — Caller verification

- **CALLERS UPDATED:** none — public names and import paths for contest shells unchanged; `RNA3D` / `arc` imports remain valid.
- Full-repo search: no references to a physical `pipeline_shells` module path under `contest/`.

PHASE 8 COMPLETE

---

=== AUDIT RESULT: level_1 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):

Same as `level_1/__init__.py` composed `__all__` (unchanged membership): contest (CLI, context, loaders, splits, argparse builders, validate-first shells from core), export (`export_model_pipeline`, metadata/source handlers), features (`create_feature_extraction_model`, `set_pretrained_weights_resolver`), grid_search (`ContestGridSearchBase`, `load_best_config_json`, `build_grid_search_context`), handlers (`get_command_handlers`), notebook (`build_run_py_base_command`, dispatch/registration, `run_cli_streaming`), paths (data/run/model/submission path helpers, `is_kaggle_input`), pipelines (`ValidateTrainSubmitPipelineResultShell`), registry (`ContestRegistry`, `detect_contest`, `get_contest`, `register_contest`), plus all symbols re-exported from those child packages as listed in the inventory’s aggregated export list.

CONSOLIDATED CHANGE LOG:

- Phase 1: 2 changes (contest shells source; data_loading imports)
- Phase 2: 0
- Phase 3: 0
- Phase 4: 1 (comment wording)
- Phase 5: 0 code changes (review notes only)
- Phase 6: 7 READMEs created/updated
- Phase 7: 2 import-surface fixes (`paths`); 2 reconciled intentional patterns (data_loading cycle break; export `source_handlers`)
- Phase 8: skipped — no breaking API renames

Itemized:

- `scripts/.../level_1/contest/__init__.py` — import pipeline shells from `layers.layer_0_core.level_1.pipelines`
- `scripts/.../level_1/contest/data_loading.py` — submodule imports for registry and contest IO/splits; import order tidy
- `scripts/.../level_1/export/export_model_pipeline.py` — remove “legacy” from comment
- `scripts/.../level_1/paths/__init__.py` — `is_kaggle_input` from `level_0` barrel
- `scripts/.../level_1/paths/models.py` — `contest_models_dir` from `level_0` barrel
- `scripts/.../level_1/README.md` — updated
- `scripts/.../level_1/contest/README.md` — created
- `scripts/.../level_1/paths/README.md` — created
- `scripts/.../level_1/pipelines/README.md` — created
- `scripts/.../level_1/registry/README.md` — created
- `scripts/.../level_1/handlers/commands/README.md` — created
- `scripts/.../level_1/export/README.md` — updated
- `.cursor/audit-results/competition_infra/inventories/INVENTORY_level_1.md` — note + flags corrected to match code

CALLERS TOUCHED (Phase 8):

- (none)

VIOLATIONS REQUIRING HUMAN REVIEW:

- None blocking; optional follow-up: rename `path_utils.py` for naming consistency (inventory prior flag).

ITEMS FOR HUMAN JUDGMENT:

- Whether to re-home `load_best_config_json` re-export exclusively under a “data/config” subpackage vs `grid_search/__init__.py`.
- Torch-heavy import chain in `layers.layer_0_core.level_1` remains an environment precondition for any import that loads full `level_1` (pre-existing).

=== END AUDIT RESULT: level_1 ===
