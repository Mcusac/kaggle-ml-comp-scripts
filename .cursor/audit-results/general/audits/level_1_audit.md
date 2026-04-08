---
generated: 2026-04-08
audit_scope: general
level_name: level_1
artifact_kind: audit
audit_profile: full
run_mode: default
audit_preset: single
run_id: general-stack-orchestrator-2026-04-08
pass_number: 1
---

# Audit: level_1

## Precheck reconciliation

`precheck_level_1_2026-04-08.md` reports **skipped_machine_script** (`ModuleNotFoundError: torchvision`). No machine violation list to reconcile. Import verification in this environment fails at first optional dependency import (`torchvision`); code changes below are syntactic/import-surface only and align with `python-import-surfaces.mdc`.

## Phase 1 — Functions & classes

No splits or renames applied. Structure already matches SRP for audited hotspots; further decomposition deferred (large surface).

**Change log:** (none)

## Phase 2 — Files

No renames or splits.

**Change log:** (none)

## Phase 3 — Packages

- Relative imports remain confined to `__init__.py` files (valid).
- No root-level orphan modules other than `__init__.py`.

**Change log:** (none)

## Phase 4 — Legacy & compatibility

No deprecation shims, `warnings.warn`, or TODO-remove legacy markers found under `level_1/`.

## Phase 5 — Full level review

- **Dependency rule:** After edits, logic files use `from level_0 import …` only for framework imports (no same-level `from level_1`, no deep `from level_0.subpkg`).
- **`__all__` policy:** Removed duplicate public contract from leaf module `evaluation/loss_types.py`; package API remains `evaluation/__init__.py`.

## Phase 6 — README

- `level_1/README.md`: completed missing **Contents** bullets (cli, grid_search, io, ontology, pipelines, protein); corrected **runtime** description (removed misplaced “CLI builders”); **Usage Example** now uses `path_bootstrap` + `from level_1 import (...)` barrel imports per `init-exports.mdc`.

**Change log:**

- `level_1/README.md` :: README updated :: contents completeness, usage aligned with public API

## Phase 7 — Cross-level audit (7a)

**Machine import violations:** N/A (precheck skipped).

**Manual scan:**

- **DEEP_PATH (filesystem):** Previously, many logic files used `from layers.layer_0_core.level_0 import …` instead of the public package `from level_0 import …` after `path_bootstrap`. **Fixed** in 77 modules (normalized to `from level_0 import`).
- **IMPORT_STYLE:** No `from .` / `from ..` in non-`__init__.py` logic files.
- **WRONG_LEVEL / UPWARD:** No `from level_1` inside `level_1/` logic; no imports from `level_2+`.

**Violation log (resolved):**

- `[multiple files]` :: `from layers.layer_0_core.level_0 import …` :: **DEEP_PATH / non-canonical surface** :: **replace with** `from level_0 import …` :: matches `python-import-surfaces.mdc` general stack rules.

**7b–7d:** No additional cross-level DRY/SOLID/KISS findings requiring code change in this pass.

## Phase 8 — Callers

No repository paths outside `level_1/` required updates: import spellings changed only inside `scripts/layers/layer_0_core/level_1/**/*.py`. External consumers continue to use `level_0` / `level_1` after bootstrap.

**CALLERS UPDATED:** *(none — Phase 8 internal-only)*

---

## === AUDIT RESULT: level_1 ===

audit_profile: full  
audit_preset: single  
run_mode: default  

**PUBLIC API (post-audit):** Unchanged composition: all names exported via `level_1.__init__.py` by concatenating `__all__` from subpackages `cli`, `data`, `evaluation`, `features`, `grid_search`, `guards`, `io`, `ontology`, `pipelines`, `protein`, `runtime`, `search`, `training`. With a full env (including optional deps), enumerate via: `path_bootstrap.prepend_framework_paths(); import level_1; sorted(level_1.__all__)`.

**CONSOLIDATED CHANGE LOG:**

- Phase 1: 0 code changes  
- Phase 2: 0  
- Phase 3: 0  
- Phase 4: 0  
- Phase 5: `evaluation/loss_types.py` — removed leaf `__all__` (policy)  
- Phase 6: 1 README updated (`level_1/README.md`)  
- Phase 7: Normalized **77** files from `from layers.layer_0_core.level_0 import` → `from level_0 import`  
- Phase 8: skipped — no external caller import path changes  
- Misc: `features/__init__.py` trailing whitespace removed on `BaseFeatureExtractor` import line  

**CALLERS TOUCHED (Phase 8):** *(none)*

**VIOLATIONS REQUIRING HUMAN REVIEW:** *(none from this pass)*

**ITEMS FOR HUMAN JUDGMENT:**

- Run `pytest` / import smoke tests in an environment with `torchvision` (and other optional ML deps) to validate runtime after this import normalization.

=== END AUDIT RESULT: level_1 ===
