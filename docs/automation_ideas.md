# Architecture Automation Master Checklist

**Source of truth (manual):** this file. Update it whenever a devtool is added, renamed, or retired.

**Run devtools from:** `input/kaggle-ml-comp-scripts/scripts/` so `python -m layers.layer_2_devtools...` resolves.

**`artifact_base`:** `input/kaggle-ml-comp-scripts`. Machine and audit-related outputs go under `artifact_base/.cursor/audit-results/<scope>/` (see `input/kaggle-ml-comp-scripts/.cursor/audit-results/README.md`).

**Entrypoint catalog:** [layer_2_devtools README](../scripts/layers/layer_2_devtools/README.md). Copy-paste invocations: [devtools-inventory command](../.cursor/commands/devtools-inventory.md) (`/devtools-inventory` in Cursor if the command is registered).

**Status legend:** **Implemented** (matches intent end-to-end) · **Partial** (exists but does not cover all sub-bullets, or is split across tools/rules/audits) · **Not started** (no dedicated automation in this repo yet).

---

## Devtools inventory (`level_1_impl/level_2` and related)

Runnable modules (prefer `python -m layers.layer_2_devtools.level_1_impl.level_2.<name>`; cwd `scripts/`). Parent package: `scripts/layers/layer_2_devtools/rewrite_layer0core_imports.py` rewrites `level_N` import style under a chosen root (migration helper).

| Module | Role |
|--------|------|
| `run_code_audit_pipeline` | Machine pipeline: discovery, optional precheck, general + CSIRO scans, `manifest.json` / `audit_queue.json` |
| `audit_precheck` | Per-target precheck `precheck_*.{md,json}` |
| `audit_targets` | Emit comprehensive audit queue JSON |
| `audit_rollup` | Rollup from queue JSON |
| `inventory_bootstrap` | Planner-mergeable inventory fragment |
| `audit_artifact_schema_check` | Validate `*_audit.md` (and optional precheck summaries) |
| `comprehensive_audit_emit` | Related audit emit helper |
| `scan_level_violations` | General stack (`layer_0_core`) import layering scan → `general/audits/` |
| `scan_csiro_level_violations` | CSIRO contest tree scan |
| `scan_barrel_enforcement` | Unified barrel-style import scan (general + contest + competition infra) → `general/audits/barrel_enforcement_scan_*.{md,json}` |
| `validate_layer_dependencies` | Validated layer dependency report (JSON + MD); paths printed at end of run |
| `apply_violation_fixes` | Apply bundled fixes from `level_violations_scan_*.json` (optional `--verify` rescan) |
| `verify_imports` | Resolve/verify imports across the tree |
| `test_imports` | Import test suite entry |
| `cleanup_imports` | Remove unused imports using a `check_health` JSON report |
| `check_health` | Package health: metrics, import graph, deep imports, dead code signal, etc. |
| `check_health_thresholds` | Enforce thresholds vs health JSON (CI: `--strict`) |
| `health_summary` | Summarize health run |
| `report_compare_health` / `report_complexity_targets` / `report_duplicates` / `report_srp` | Focused reports |
| `validate_before_upload` | Pre-upload checks |
| `verify_hyperparameter_recommendations` / `analyze_hyperparameters` | Hyperparameter workflows |
| `regenerate_package_inits` | Deterministic `__init__.py` regen for a `--root` tree |
| `clean_pycache` | Hygiene |
| `package_dumping` | Package dump utilities (`package_dumping/` subpackage) |

---

# 1. Core Architecture Enforcement (Highest Priority)

## 1.1 Dependency Level Violation Detector

**Status:** **Partial** (general stack is complete; `validate_layer_dependencies` remains a **separate** devtools+`dev` bucket graph, not a second pass over all of `layer_0_core`).

**Entrypoint(s):** `scan_level_violations` (general stack `layer_0_core`); `validate_layer_dependencies` (bucket ranks for `layer_2_devtools` and optional `dev` only); `scan_csiro_level_violations` (CSIRO); `apply_violation_fixes` consumes `level_violations_scan_*.json`. **`run_code_audit_pipeline`** can run precheck + scans and record results in a manifest (orchestrated run).

**Artifacts:** e.g. `general/audits/level_violations_scan_*.{md,json}` (JSON `schema: level_violations_scan.v2` with per-violation `file_level` / `imported_level` / `suggested_min_level` when applicable); optional `level_violations_move_plan_<date>.md` via `--emit-move-plan`. Machine runs under `general/summaries/machine_runs/<run_id>/`. `validate_layer_dependencies` prints dependency report paths on success.

**Owner:** Devtools CLIs; import rules canonical in `level_0_infra/level_0/validation/import_rules/general_rules.py` (tuple classifier); code-audit for policy narrative beyond the scan.

* [x] Parse file level from path
* [x] Parse imports and determine highest level referenced
* [x] Compare file level vs import level
* [x] Output violations
* [x] Suggest correct level for file relocation (heuristic: `suggested_min_level` on `WRONG_LEVEL` / `UPWARD` / some `DEEP_PATH` rows in JSON)
* [x] Optional: generate move plan (draft checklist: `scan_level_violations --emit-move-plan`, no auto-moves)
* [~] Optional: CI fail on violation — `scan_level_violations --json --fail-on-violations` (optional step in `.github/workflows/health-check.yml` with `continue-on-error: true` until the tree is clean; remove to block)

---

## 1.2 Barrel Enforcement Checker

**Status:** **Implemented** (machine checks in devtools; code-audit `profile barrels` remains the human pass)

**Entrypoint(s):** `python -m layers.layer_2_devtools.level_1_impl.level_2.scan_barrel_enforcement` (same defaults as `scan_csiro_level_violations` for the CSIRO contest root). API: `layers...level_1.api_audit.run_barrel_enforcement_with_artifacts`. Policy: `input/kaggle-ml-comp-scripts/.cursor/rules/python-import-surfaces.mdc` (e.g. no mixing `layers.layer_0_core.*` with short `from level_N import` in the same file; infra barrel bypass `INFRA_BARREL_DEEP`). `regenerate_package_inits` keeps `__init__.py` surfaces consistent.

**Artifacts:** `artifact_base/.cursor/audit-results/general/audits/barrel_enforcement_scan_<date>.{md,json}` with `schema: barrel_enforcement_scan.v1` and per-row `scope` (`general` | `contest` | `infra`), plus `by_scope` counts. **Code-audit** `profile barrels` (orchestrated) for narrative/convention review.

**Owner:** Devtools + rules; `regenerate_package_inits` for export lists; code-audit for policy beyond the scanner.

* [x] Detect deep / barrel-bypass patterns covered by `general_scan_ops`, `contest_scan_ops`, `infra_scan_ops` (e.g. `LAYER0_CORE_MIXED_IMPORT_STYLE`, `CONTEST_DEEP_PATH`, `INFRA_BARREL_DEEP`)
* [x] Unified machine-readable report (merged JSON + markdown)
* [~] Suggest correct barrel import (suggestions in violation text; no dedicated autofix for all cases)
* [~] Optional auto-fix (partial: `apply_violation_fixes` / import rewrites where applicable; not all barrel cases)
* [~] Optional CI: `scan_barrel_enforcement --json` in `.github/workflows/health-check.yml` with `continue-on-error: true` (same pattern as `scan_level_violations`)

---

## 1.3 Circular Dependency Detector

**Status:** **Implemented** (dedicated)

**Entrypoint(s):** `python layers/layer_2_devtools/level_1_impl/level_2/circular_deps.py` (cwd `scripts/`). Optional wrapper: `python layers/layer_2_devtools/entrypoints/circular_deps.py`.

**Artifacts:** `general/audits/circular_deps_scan_<date>.{md,json}` (JSON `schema: circular_deps_scan.v1`).

* [~] Build import graph (partial: health / other analyzers)
* [x] Run cycle detection (clear cycle chains as first-class output)
* [x] Print cycle chain
* [x] CI fail on cycles (`--fail-on-cycles`)

---

## 1.4 Layer Dependency Graph Generator

**Status:** **Implemented** (dedicated)

**Entrypoint(s):** `python layers/layer_2_devtools/level_1_impl/level_2/layer_dependency_graph.py` (cwd `scripts/`). Optional wrapper: `python layers/layer_2_devtools/entrypoints/layer_dependency_graph.py`.

**Artifacts:** `general/audits/layer_dependency_graph_<date>.md`

* [x] Build dependency adjacency map
* [x] Print text graph (markdown)
* [ ] Optional Graphviz output
* [x] Highlight violations (`--fail-on-violations`)

---

# 2. Import Validation & Fixing

## 2.1 Import Path Validator

**Status:** **Implemented** (strict policy; suggestions are conservative)

**Entrypoint(s):** `verify_imports`; `test_imports`.

**Owner:** Devtools.

* [x] Compare import targets to on-disk module paths (internal modules only; filesystem-based)
* [x] Detect policy mismatches (relative imports in logic files; deep `level_N.*`; wrong-level and upward `level_N` usage)
* [~] Resolve symbol location (limited: parses `__init__.py` exports for barrel suggestions; not a full canonical symbol resolver)
* [~] Suggest correct import (conservative: barrel suggestion only when provable via exports / relative import level heuristics)

---

## 2.2 Import Auto-Fixer

**Status:** **Implemented** (rewrite-only; barrel regeneration is a separate tool)

**Entrypoint(s):** `fix_imports` (new rewrite-only auto-fixer); `apply_violation_fixes` (legacy bundled move+patch fixes); `rewrite_layer0core_imports` at `layer_2_devtools/rewrite_layer0core_imports.py` (scoped migration). Pair with `regenerate_package_inits` as a separate step when a missing export prevents safe barrel rewrites.

* [x] Parse AST (where used in violation fix / maintenance APIs)
* [x] Resolve canonical symbol path (conservative: use `level_N/__init__.py` exports only)
* [x] Replace import (conservative: single-line import rewrites only, drift-safe)
* [x] Preserve formatting (best effort in rewrite utilities)
* [x] Respect barrel rules (rewrite-only; does not modify barrels)

---

## 2.3 Import Organizer

**Status:** **Implemented** (policy + deterministic rewrite-only devtool)

**Entrypoint(s):** Policy: `input/kaggle-ml-comp-scripts/.cursor/rules/python-import-order.mdc`. Devtool: `python -m layers.layer_2_devtools.level_1_impl.level_2.organize_imports` (cwd `scripts/`). API: `run_import_organizer_cli_api` (maintenance).

* [x] Extract top-of-file import region (docstring + `__future__` aware)
* [x] Categorize into groups 1–5 (per `python-import-order.mdc`)
* [x] Stable sort (module path, numeric-aware `level_N`)
* [x] Rewrite import block only (span-safe; preserves newline style)
* [x] Unit tests (`test_import_organizer_unittest.py`)

---

## 2.4 Global Import Cleaner

**Status:** **Implemented** (report-driven; optional external formatter)

**Entrypoint(s):** `check_health` reports unused imports; `cleanup_imports --report <health_report.json>` applies removals. Typical flow: `check_health --json` → `cleanup_imports`.

* [x] Detect unused imports
* [x] Remove them (with `--report`, drift-safe span edits; multiline-aware)
* [x] Organize top-of-file imports deterministically (internal organizer)
* [x] Optional external formatter pass (default off): `cleanup_imports --format --format-tool ruff|black`

---

# 3. Barrel / **init** Automation

## 3.1 **init** Regeneration

**Status:** **Implemented** (regenerate + check + dry-run; policy-aligned export inference)

**Entrypoint(s):** `regenerate_package_inits` (`--fix` / `--check` / `--dry-run`, optional `--report-nonlocal`, `--exclude-symbol`, `--include-symbol`).

**Owner:** Devtools.

* [x] Rebuild exports
* [x] Validate exports exist (derived from leaf-module AST definitions; `--check` validates drift vs generator)
* [x] Remove stale exports (regen overwrites per policy)
* [x] Enforce ordering (deterministic regen)
* [x] Default-safe export filtering (exclude CLI-ish names like `main`; override with `--include-symbol main`)
* [x] Nonlocal import detector for existing barrels (`--report-nonlocal`)

---

## 3.2 Public Symbol Export Checker

**Status:** **Implemented**

**Entrypoint(s):** `python -m layers.layer_2_devtools.level_1_impl.level_2.public_symbol_export_checker` (standalone checker). Related: `regenerate_package_inits` (fixer: deterministic regen).

* [x] Scan definitions
* [x] Compare to **init**
* [x] Suggest export additions

---

# 4. Dead Code & Symbol Detection

## 4.1 Dead Symbol Detector

**Status:** **Implemented**

**Entrypoint(s):** `python -m layers.layer_2_devtools.level_1_impl.level_2.dead_symbol_detector` (orchestrator); focused tools: `dead_symbols_unreferenced`, `dead_symbols_unreachable`. Related: `check_health` / `health_summary` (dead code = unused imports + unreachable blocks, not symbol reachability).

* [x] Collect definitions (public top-level `class`/`def`/`async def`/constants)
* [x] Collect references (alias-aware, conservative resolution)
* [x] Unreferenced scan (definitions with zero resolved references; self-references excluded)
* [x] Unreachable-from-entrypoints scan (reachability on symbol graph; configurable entrypoints)
* [x] Orchestrator run (single pass; combined report)
* [x] Output JSON + MD artifacts under `artifact_base/.cursor/audit-results/general/audits/`
* [x] Unit tests (devtools unit suite)

---

## 4.2 Dead File Detector

**Status:** **Implemented**

**Entrypoint(s):** `python layers/layer_2_devtools/level_1_impl/level_2/dead_file_detector.py` (dedicated report); `check_health` still surfaces orphaned modules in its imports section (health JSON: `imports.orphans`).

* [x] Build import graph (reuses `ImportAnalyzer` / health import map)
* [x] Detect isolated files (two views: orphans + unreachable-from-entrypoints)
* [x] Suggest deletion (report-only candidates; no auto-delete or rm-plan)

---

## 4.3 Unreachable Module Detector

**Status:** **Implemented**

**Entrypoint(s):** `python layers/layer_2_devtools/level_1_impl/level_2/unreachable_module_detector.py --help` (module graph reachability + cascade + SCC clusters; emits `unreachable_module_detector_run_*.{md,json}`).

**Existing (implemented as part of Dead File Detector and shared infra):**

* [x] Unreachable-from-entrypoints scan (module import graph reachability)
* [x] Entrypoint + allowlist config model (`DeadFileConfig`)
* [x] Report-only artifacts (MD + optional JSON) with basic removal caveats
* [x] Unit test coverage (via `test_dead_file_detector.py`)

**Added (standalone devtool):**

* [x] Cascade dead detection (waves) — orphan-cascade candidates (iterative peel)
* [x] SCC grouping for cleanup ordering (mutually-referential clusters)
* [x] Suggest cleanup (conservative ordering + risk flags; no destructive actions)
* [x] Dedicated `unreachable_module_detector` entrypoint + schema (`unreachable_module_detector_run.v1`)
* [x] Dedicated unit tests (`test_unreachable_module_detector.py`)

---

# 5. Layer Placement Suggestions

## 5.1 File Level Suggestion Tool

**Status:** **Partial** (general-stack scan has heuristics; dedicated multi-scope engine now implemented)

* [x] Analyze dependencies (import graph + incoming edges via health analyzer `ImportAnalyzer`)
* [x] Compute minimal valid level (outgoing LB + incoming UB constraints; conflicts reported) — `file_level_suggestions`
* [x] Suggest relocation (report-only target `level_N`; emits MD/JSON + wave plan) — `file_level_suggestions_orchestrate`
* [x] Draft move checklist from level-violation scan payload (`scan_level_violations --emit-move-plan`)

---

## 5.2 Promotion Suggestion Tool

**Status:** **Implemented** (report-only)

**Entrypoint(s):**
- `python -m layers.layer_2_devtools.level_1_impl.level_2.promotion_suggestions`
- `python -m layers.layer_2_devtools.level_1_impl.level_2.promotion_demotion_suggestions_orchestrate`

**Artifacts:** `artifact_base/.cursor/audit-results/<scope>/audits/promotion_demotion_suggestions_<scope>_<date>.{md,json}`

* [x] Count cross-level usage (inbound-by-level via scope-normalized imports)
* [x] Detect heavy reuse (thresholds: total inbound, distinct importers, distinct levels)
* [x] Recommend promotion (promotion = move to a higher `level_N`, bounded and report-only)

---

## 5.3 Demotion Suggestion Tool

**Status:** **Implemented** (report-only)

**Entrypoint(s):**
- `python -m layers.layer_2_devtools.level_1_impl.level_2.demotion_suggestions`
- `python -m layers.layer_2_devtools.level_1_impl.level_2.promotion_demotion_suggestions_orchestrate`

**Artifacts:** `artifact_base/.cursor/audit-results/<scope>/audits/promotion_demotion_suggestions_<scope>_<date>.{md,json}`

* [x] Check if only used by lower layer (all inbound importer levels strictly lower than current)
* [x] Suggest demotion (demotion = move to a lower `level_N`, bounded and report-only)

---

# 6. Structure Hygiene

## 6.1 Deep Nesting Detector

**Status:** **Implemented**

**Entrypoint(s):**
- `python -m layers.layer_2_devtools.level_1_impl.level_2.deep_nesting_detector`
- `python -m layers.layer_2_devtools.level_1_impl.level_2.check_health` (includes `deep_nesting` section)
- `python -m layers.layer_2_devtools.level_1_impl.level_2.check_health_thresholds` (enforces `max_directory_depth` and `max_deep_directories`)

**Artifacts:** `artifact_base/.cursor/audit-results/general/audits/deep_nesting_scan_<date>.{md,json}` (standalone); deep nesting also appears in `check_health` JSON under `deep_nesting`.

* [x] Count directory depth (code-containing directories; depth relative to `--root`)
* [x] Flag beyond threshold (health thresholds: `max_directory_depth`, `max_deep_directories`)

---

## 6.2 Oversized Module Detector

**Status:** **Implemented** (`check_health` file metrics + thresholds, plus dedicated `oversized_module_detector` artifacts; wired into `run_code_audit_pipeline`)

**Entrypoint(s):**
- `python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --json` (emits `file_metrics.file_lines` / `file_metrics.long_files`)
- `python -m layers.layer_2_devtools.level_1_impl.level_2.check_health_thresholds <health_report.json> --strict` (enforces `ThresholdConfig.max_file_lines`)
- `python -m layers.layer_2_devtools.level_1_impl.level_2.oversized_module_detector --json` (writes `oversized_module_scan_<date>.{md,json}`)
- Machine pipeline: `python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline` (manifest step: `oversized_module_scan`)

**Artifacts:** `artifact_base/.cursor/audit-results/general/audits/oversized_module_scan_<date>.{md,json}` (`schema: oversized_module_scan.v1`)

* [x] Count LOC / file lines (`FileMetricsAnalyzer`)
* [x] Enforce max file lines (`ThresholdConfig.max_file_lines` via `check_health_thresholds`)
* [x] Emit dedicated oversized-module report (MD/JSON artifacts)
* [x] Suggest splitting (heuristic, report-only)

---

## 6.3 Package Boundary Validator

**Status:** **Implemented** (single boundary validator + matrix report; preserves existing layered tools)

**Entrypoint(s):**
- `python layers/layer_2_devtools/entrypoints/package_boundary_validator.py` (writes MD/JSON artifacts)
- Machine pipeline: `python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline --run-package-boundary` (manifest step: `package_boundary_validation`)

**Artifacts:** `artifact_base/.cursor/audit-results/general/summaries/package_boundary_validation_<date>.{md,json}` (`artifact: package_boundary_validation`)

* [x] Define allowed boundaries (rules + boundary spec/classifier)
* [x] Detect violations (single scan across `scripts/layers` + optional `scripts/dev`)
* [x] Forbidden/allowed “boundary matrix” report (counts + violating examples)

---

# 7. Refactor Safety Tools

## 7.1 Impact Scanner

**Status:** **Implemented**

**Entrypoint(s):** `python layers/layer_2_devtools/level_1_impl/level_2/impact_scanner.py`

* [x] List inbound imports (one-shot per file)
* [x] List outbound imports (one-shot per file)
* [x] Print dependency tree (forward + reverse, bounded)
* [x] Save optional MD/JSON artifact (`impact_scan_<date>.{md,json}` under `general/audits/`)

---

## 7.2 Safe Move Planner

**Status:** **Implemented** (single + batch; safe move + conservative rewrites + optional barrel regen + optional verify)

* [x] Compute new path (library: `level_0_infra.level_0.moves.compute_move_plan`)
* [x] Move file safely (dry-run default; refuse overwrite; create destination dirs)
* [x] Rewrite imports (drift-safe line edits; supports multiline `from ... import (` by rewriting the header line only)
* [x] Update barrels (optional integration with `regenerate_package_inits`)
* [x] Verify (optional integration with `verify_imports`)

---

# 8. Orchestrators

## 8.1 Audit Orchestrator

**Status:** **Implemented**

**Entrypoint(s):**
- Chat: `/code-audit` and `code-audit` agent flow (planner/auditor/runner) per `code-audit-delegation.mdc`.
- Machine (v2): `python -m layers.layer_2_devtools.level_1_impl.level_2.audit_orchestrator` (manifest example: `level_1_impl/level_2/code_audit_orchestrator_manifest.v2.example.json`).
- Machine (v1, legacy/CI parity): `python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline` (manifest example: `level_1_impl/level_2/code_audit_pipeline_manifest.v1.example.json`).

**Sub-checks:** The checklist below represents the v2 machine orchestrator’s guaranteed steps (independently toggleable).

* [x] dependency check (scans + validation in devtools; extent varies)
* [x] import validation (verify-imports scan + barrel enforcement)
* [x] circular deps
* [x] barrel violations
* [x] dead symbols

---

## 8.2 Fix Orchestrator

**Status:** **Implemented**

**Entrypoint(s):** `/code-fix` and `code-fix` per `code-fix-delegation.mdc` (tool-first; `FIX_RUN_*.md` in summaries). Machine pipeline: `python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_fix_pipeline` (deterministic; dry-run default; emits `FIX_RUN_*.md`). Tools composed as applicable: `apply_violation_fixes`, `fix_imports`, `cleanup_imports`, `organize_imports`, `regenerate_package_inits`, `verify_imports`.

* [x] rewrite imports
* [x] organize imports
* [x] regenerate barrels (init regen)

---

## 8.3 CI Runner

**Status:** **Implemented** (devtool + GitHub Actions)

**Entrypoint(s):** `python -m layers.layer_2_devtools.level_1_impl.level_2.ci_runner` (canonical) and `.github/workflows/health-check.yml` (wiring). Weekly schedule: Monday 00:00 UTC (`cron` in same file).

* [x] run fast checks (pipeline + level violations + barrel enforcement + health + thresholds)
* [x] fail on violations (blocking scans + strict thresholds; manifest upload is best-effort)
* [x] print summary (job summary + artifacts + `.cursor/.../ci_runs/<run_id>/summary.md`)

---

# 9. CI Integration (.github)

## 9.1 Required CI Checks

**Status:** **Implemented** (see workflows)

* [x] dependency violations (via pipeline + scans; not identical to a standalone `validate_layer_dependencies` job)
* [x] circular dependencies (wired into `ci_runner` → `api_ci.run_ci_runner`)
* [x] barrel enforcement (wired into `ci_runner` and the health-check workflow)
* [x] import validation (wired into `ci_runner` via `verify_imports`; optional runtime probe via `test_imports` as separate job if desired)

---

## 9.2 Warning-only CI Checks

**Status:** **Implemented** as a separate workflow (`ci-warnings.yml`) (non-blocking).

* [x] dead symbols (`dead_symbol_detector`, report-only)
* [x] promotion/demotion suggestions (`promotion_demotion_suggestions_orchestrate`, report-only)
* [x] deep nesting (report-only; **gating remains in health thresholds**, this is for details)

---

## 9.3 Scheduled CI Jobs

**Status:** **Implemented** — dedicated scheduled workflows exist (nightly + weekly).

* [x] nightly full audit (`nightly-audit.yml`)
* [x] nightly auto-fix dry-run (`nightly-fix-dry-run.yml`)
* [x] weekly cleanup report (`weekly-cleanup-report.yml`) (distinct from health artifact upload)

---

# 10. Reporting Tools

## 10.1 Markdown Report Generator

**Status:** **Implemented** — consolidated markdown scorecards are available (health report JSON or audit/pipeline manifest JSON), in addition to existing per-tool `.md` + JSON artifacts.

* [x] print violations
* [x] group by category (single scorecard groups health sections + manifest step summary + artifact links)
* [x] save audit report (machine + human + consolidated scorecard)
* [x] unified scorecard markdown from existing artifacts (`report_scorecard --health-report ...` or `--manifest ...`)

---

## 10.2 Summary Score Generator

**Status:** **Implemented** — numeric architecture score (0–100) computed from health JSON or manifest JSON; optional JSON config override.

* [x] count violations
* [x] compute architecture health score (`report_score --health-report ...` or `--manifest ...`)
* [x] emit score JSON for CI/regression tracking (`report_score --write`)

---

# 11. Nice-to-Have (Future)

* [ ] dependency heatmap
* [ ] architecture drift detector
* [ ] refactor candidate ranking
* [ ] unused barrel export detector
* [ ] inconsistent naming detector
* [ ] test coverage vs layer report
* [ ] code ownership per layer
* [ ] layer coupling metrics

---

# Progress Tracking

## Completed

* [x] `__init__` regeneration (`regenerate_package_inits`)
* [x] Code audit machine pipeline with manifest/queue (`run_code_audit_pipeline`)
* [x] General stack level violation scan (`scan_level_violations` + JSON, `suggested_min_level`, `--emit-move-plan`, `--fail-on-violations`)
* [x] Layer dependency validation report (`validate_layer_dependencies`)
* [x] Health JSON + strict thresholds in CI (`check_health` + `check_health_thresholds`)
* [x] CI workflow wiring (`.github/workflows/health-check.yml`)

## In progress / partial (see section statuses above)

* Import/barrel/cycle “single tool” coverage; move planner; import organizer; warning-only jobs.

## Not started

* Remaining items still marked **Not started** in sections 10–11 (e.g. single-number “architecture health score”, optional heatmaps / drift detectors).

---

# Recommended Build Order

1. Dependency level detector (extend/polish: **done in large part** — see 1.1)
2. Barrel enforcement checker (tighten machine checks vs audits-only)
3. Dead symbol detector (optional: split from `check_health` or formalize its output)
4. Import validator (consolidate `verify_imports` + test suite expectations)
5. Import organizer (script or ruff/formatter integration; align with `python-import-order.mdc`)
6. Circular dependency detector
7. Promotion suggestions
8. CI integration (**partial** — extend jobs as needed)
9. Auto import fixer (**partial** — `apply_violation_fixes` and related)
10. Reporting tools (**partial** — add unified markdown scorecard if desired)

---
