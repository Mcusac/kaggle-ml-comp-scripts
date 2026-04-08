---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_2
pass_number: 1
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
run_id: comp_infra_overhaul_2026-04-08
---

# Audit: level_2 (competition infra)

**level_path:** `scripts/layers/layer_1_competition/level_0_infra/level_2`  
**Inventory:** `competition_infra/inventories/INVENTORY_level_2.md` (updated post-audit)  
**Precheck:** `competition_infra/summaries/precheck_level_2_2026-04-08.md` — clean (INFRA_TIER_UPWARD, INFRA_GENERAL_LEVEL, DEEP_PATH, RELATIVE_IN_LOGIC, PARSE_ERROR all zero)  
**Prior:** `level_0_audit.md`, `level_1_audit.md` — barrels for `level_0` / `level_1`; prefer infra package imports; `create_feature_extraction_model` and `ContestRegistry` remain the correct `level_1` surfaces.

## Phase 1 — Functions & Classes

### Findings

- `FeatureExtractionHelper` lived in a module named `helpers`, which violates coding-standards naming (“what does this do?” vs catch-all).
- Module docstring referenced `FeatureExtractionTrainer`, which is not defined in this tier (trainer lives in `level_3`).

### Changes applied

- `feature_extraction/helpers.py` → `feature_extraction/feature_extraction_helper.py` :: **naming / SRP** :: file name matches the owning type and purpose; drop catch-all `helpers`.
- `feature_extraction_helper.py` :: module docstring :: **accuracy** :: describes joint feature/target extraction only.

PHASE 1 COMPLETE

## Phase 2 — Files

- `helpers.py` → `feature_extraction_helper.py` :: **reason** :: same as Phase 1; no split/merge needed elsewhere.

PHASE 2 COMPLETE

## Phase 3 — Packages & Sub-packages

- Sub-packages `feature_extraction/` and `registry/` remain concept-grouped; no root-level logic files other than `__init__.py`.
- `level_2/__init__.py` module docstring updated to describe this tier accurately (utilities + CLI registry, not the two-stage trainer).

PHASE 3 COMPLETE

## Phase 4 — Legacy & Compatibility Purge

No legacy or compatibility code found.

PHASE 4 COMPLETE

## Phase 5 — Full Level Review

- **Imports:** `test_extractor.py` now uses top-of-file `load_json` and `python-import-order.mdc` grouping (`import numpy` before `from pathlib` / `from typing`).
- **Registry:** `cli_handlers.py` already matched stdlib grouping (bare `import` then `from`); no logic change.
- **Cross-level docs:** `level_3/trainer/__init__.py` claimed `FeatureExtractionTrainer` was re-exported from `level_2.feature_extraction`; corrected to reflect actual layout (`level_3` owns the trainer).
- **Dependency rule (infra tier K = 2):** Imports are limited to `layers.layer_0_core.*` and `layers.layer_1_competition.level_0_infra.level_1` only — no `level_3+` infra, no upward contest tiers.

PHASE 5 COMPLETE

## Phase 6 — README & Documentation

| Path | Change |
|------|--------|
| `level_2/README.md` | README updated :: purpose, contents, API, dependencies, example aligned with code; documents that trainer is `level_3` |
| `level_2/feature_extraction/README.md` | README updated :: removed stale trainer/config narrative; documented `feature_extraction_helper.py` + `test_extractor.py` |
| `level_2/registry/README.md` | README created :: Purpose, Contents, Public API, Dependencies, Usage Example (CSIRO `level_7.handlers` path) |

PHASE 6 COMPLETE

## Phase 7 — Cross-Level Audit (competition_infra, tier K = 2)

### Precheck reconciliation

- Machine precheck listed no violations; post-edit manual pass unchanged — **7a-contest** surfaces still use `level_0_core` and `level_0_infra.level_1` barrels only.
- **INFRA_DEEP_PATH / CONTEST_DEEP_PATH:** none — `create_feature_extraction_model`, `ContestRegistry`, core symbols use package-root forms.

### 7a-contest — Import surfaces

- No `INFRA_TIER_UPWARD` (no imports from `level_0_infra/level_3+`).
- `test_extractor.py` :: `from layers.layer_0_core.level_4 import load_json` :: **VALID** :: public `level_4` API.

### 7b–7d

- No duplicated lower-level logic identified; `FeatureExtractionHelper` is a thin adapter over core `FeatureExtractor` (appropriate).

**Violation log:** No import violations found.

PHASE 7 COMPLETE

## Phase 8 — Caller verification and repository consistency

- Public symbol names and `level_2` barrel paths are **unchanged**; internal module rename does not affect callers (nothing imported `…feature_extraction.helpers`).
- **Doc-only fix** in higher tier to remove stale cross-reference: `level_3/trainer/__init__.py`.

CALLERS UPDATED:

- `scripts/layers/layer_1_competition/level_0_infra/level_3/trainer/__init__.py` :: module docstring only (trainer location vs `level_2`)

PHASE 8 COMPLETE

---

=== AUDIT RESULT: level_2 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):

- **FeatureExtractionHelper** — Wraps core `FeatureExtractor` for joint feature and target extraction from a dataloader.
- **extract_test_features_from_model** — Build feature model and test loader, extract test features, free GPU resources.
- **find_feature_filename_from_ensemble_metadata** — Resolve `feature_filename` from ensemble models’ `model_metadata.json`.
- **register_cli_handlers_module** — Attach CLI handlers module path to a `ContestRegistry` entry.
- **list_contests_with_cli_handlers** — Contest keys with a registered CLI handlers module.
- **get_cli_handlers_module** — Import and return the handlers module for a contest.

CONSOLIDATED CHANGE LOG:

- Phase 1: 2 (module rename rationale + docstring)
- Phase 2: 1 (file rename)
- Phase 3: 1 (`level_2` root docstring)
- Phase 4: 0
- Phase 5: 2 (`test_extractor` import order + `level_3` trainer docstring)
- Phase 6: 3 READMEs (2 updated, 1 created)
- Phase 7: 0 violations; precheck reconciled
- Phase 8: 1 file (docstring only)

Itemized:

- `scripts/.../level_0_infra/level_2/feature_extraction/helpers.py` — **removed** (replaced by `feature_extraction_helper.py`)
- `scripts/.../level_0_infra/level_2/feature_extraction/feature_extraction_helper.py` — **added** (moved content, revised docstring)
- `scripts/.../level_0_infra/level_2/feature_extraction/__init__.py` — import `FeatureExtractionHelper` from new module
- `scripts/.../level_0_infra/level_2/feature_extraction/test_extractor.py` — top-level `load_json`; import order
- `scripts/.../level_0_infra/level_2/__init__.py` — package docstring
- `scripts/.../level_0_infra/level_2/README.md` — rewritten to match implementation
- `scripts/.../level_0_infra/level_2/feature_extraction/README.md` — rewritten
- `scripts/.../level_0_infra/level_2/registry/README.md` — created
- `scripts/.../level_0_infra/level_3/trainer/__init__.py` — docstring fix (trainer ownership)
- `.cursor/audit-results/competition_infra/inventories/INVENTORY_level_2.md` — tree + file entries + flags

CALLERS TOUCHED (Phase 8):

- `scripts/layers/layer_1_competition/level_0_infra/level_3/trainer/__init__.py`

VIOLATIONS REQUIRING HUMAN REVIEW:

- None.

ITEMS FOR HUMAN JUDGMENT:

- Full import smoke test in this workspace failed before reaching `level_2` (torch unavailable — `BaseVisionModel` annotation). Re-run import/tests in an environment with project dependencies installed.

=== END AUDIT RESULT: level_2 ===
