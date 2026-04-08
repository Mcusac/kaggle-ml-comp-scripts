---
generated: 2026-04-08
audit_scope: general
level_name: level_0
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: audit
audit_profile: full
audit_preset: single
run_mode: default
precheck_report_path: ../summaries/precheck_level_0_2026-04-08.md
inventory_path: ../inventories/INVENTORY_level_0.md
---

# Audit: level_0

## Pre-flight

- **Inventory:** `INVENTORY_level_0.md` — complete; header `INVENTORY: level_0` present.
- **Rules read:** `python-import-surfaces.mdc`, `python-import-order.mdc`, `architecture.mdc`, `coding-standards.mdc`, `init-exports.mdc`.
- **Precheck:** Machine precheck **skipped** (`torchvision` missing in audit environment). No violation checklist to reconcile in Phase 7.

## PHASE 1 — Functions & Classes

- No splits/renames required. Types and functions align with single-purpose boundaries per inventory review.
- **Change log:** none applied beyond documentation and package aggregation (Phase 3/6).

**PHASE 1 COMPLETE**

## PHASE 2 — Files

- No file splits/merges. Largest modules (`result_selection.py`, `submission.py`) remain cohesive.
- **Change log:** none.

**PHASE 2 COMPLETE**

## PHASE 3 — Packages & Sub-packages

- **vision/__init__.py** — Updated to follow `init-exports.mdc` nested-subpackage pattern: `from . import image`, `from .image import *`, and `__all__ = list(image.__all__) + [...]` for sibling leaf exports. Avoids hand-duplicating image symbol names at the aggregation layer.

**Change log:**

- `level_0/vision/__init__.py` → composed `__all__` from `image.__all__` + explicit leaf symbols :: align with init-exports Layer 2

**PHASE 3 COMPLETE**

## PHASE 4 — Legacy & Compatibility Purge

- No `DeprecationWarning`, shims, or compatibility branches found in `level_0` Python sources (grep).
- **Change log:** `No legacy or compatibility code found.`

**PHASE 4 COMPLETE**

## PHASE 5 — Full Level Review

- **Dependency rule:** `level_0` has no upward framework imports; same-level logic uses relative imports only in `__init__.py` (per conventions). No circular import issues identified in spot checks.
- **Root `__init__.py`:** Continues to aggregate subpackages with composed `__all__`; no change.
- **Human review:** Wide star-export surface at `level_0` root is intentional barrel design; consumers should still prefer stable names in `level_0.__all__` only.

**PHASE 5 COMPLETE**

## PHASE 6 — README & Documentation

**Change log:**

- `level_0/abstractions/README.md` :: README updated :: document all exported types (`NamedRegistry`, `PipelineResult`, `Metric`, `EnsemblingMethod`, etc.) and module list
- `level_0/cli/README.md` :: README updated :: `comma_separated_type`, `parse_key_value_pairs` in Contents/Public API
- `level_0/vision/README.md` :: README updated :: `model_type`, `transform_constants`, `TransformMode.TTA`, deps (cv2, optional torchvision)
- `level_0/vision/image/README.md` :: README updated :: usage via `from level_0 import …`; cv2 note
- `level_0/grid_search/README.md` :: README updated :: removed non-existent `pareto_frontier`; added `results_payload`, `filter_successful_results`, `worst_case_metric_sentinel`
- `level_0/README.md` :: README updated :: abstractions row matches full public surface

**PHASE 6 COMPLETE**

## PHASE 7 — Cross-Level Audit

**SKIPPED** (`audit_scope: general` and `level_number: 0` — no `from level_N` layering for the general stack).

Precheck machine reconciliation: **N/A** (precheck script did not run).

**PHASE 7 COMPLETE**

## PHASE 8 — Caller verification

- **No** renames, signature changes, or public symbol removals in Python modules.
- **Callers updated:** none (documentation-only and internal `vision` `__all__` composition; exported names unchanged).

**PHASE 8 COMPLETE**

---

```
=== AUDIT RESULT: level_0 ===
audit_profile: full
audit_preset: single
run_mode: default

PUBLIC API (post-audit):
  Unchanged: 173 names exported from `level_0.__all__` (subpackages: abstractions, cli, config, embeddings, errors, grid_search, ontology, paths, prediction_guards, protein_features, runtime, scoring, training, vision). Full sorted list available via `import path_bootstrap; path_bootstrap.prepend_framework_paths(); import level_0; sorted(level_0.__all__)`.

CONSOLIDATED CHANGE LOG:
  Phase 1: 0 code changes
  Phase 2: 0
  Phase 3: 1 — vision/__init__.py __all__ composition from image subpackage
  Phase 4: 0
  Phase 5: 0
  Phase 6: 6 READMEs updated (abstractions, cli, vision, vision/image, grid_search, level_0 root)
  Phase 7: skipped (level_0)
  Phase 8: skipped — no API changes affecting callers

CALLERS TOUCHED (Phase 8):
  (none)

VIOLATIONS REQUIRING HUMAN REVIEW:
  - None in code; precheck unavailable in audit environment (install optional deps locally to enable machine scan).

ITEMS FOR HUMAN JUDGMENT:
  - Whether to narrow `level_0` root re-exports over time (currently full barrel).

=== END AUDIT RESULT: level_0 ===
```
