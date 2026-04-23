# Devtools (`layer_2_devtools`)

**Automation checklist (have vs planned):** [`docs/automation_ideas.md`](../../../docs/automation_ideas.md) — update when you add a new `level_2` tool.

**Working directory:** `kaggle-ml-comp-scripts/scripts/` (the package root that contains `layers/` on `sys.path`).

## Canonical `python -m` entrypoints

Implementation modules live under [`level_1_impl/level_2/`](level_1_impl/level_2/). Prefer:

`python -m layers.layer_2_devtools.level_1_impl.level_2.<module>`

| Module | Role |
|--------|------|
| `audit_precheck` | Writes `precheck_*.md` / `.json` under `artifact_base/.cursor/audit-results/.../summaries/` |
| `audit_artifact_schema_check` | Validates `*_audit.md` and optional `--precheck-summaries` |
| `audit_targets` | Emits JSON queue for comprehensive orchestration |
| `audit_rollup` | Rollup from queue JSON |
| `run_code_audit_pipeline` | Machine runner: discovery + optional precheck/scans; writes [`code_audit_pipeline_manifest.v1.example.json`](level_1_impl/level_2/code_audit_pipeline_manifest.v1.example.json)–shaped `manifest.json` under `artifact_base/.cursor/audit-results/.../machine_runs/<run_id>/` |
| `audit_orchestrator` | Full audit orchestrator (8.1): composes checks into a manifest v2 run (example manifest: [`code_audit_orchestrator_manifest.v2.example.json`](level_1_impl/level_2/code_audit_orchestrator_manifest.v2.example.json)) |
| `ci_runner` | CI runner (8.3): pipeline + blocking scans + health + thresholds; writes `health_report.json` to workspace root and a summary under `.cursor/audit-results/.../ci_runs/<run_id>/` |
| `inventory_bootstrap` | Planner merge fragment |
| `validate_before_upload` | Pre-upload checks |
| `check_health` / `check_health_thresholds` | Health reports |
| `scan_barrel_enforcement` | Merged barrel/import-surface scan (`barrel_enforcement_scan_*.{md,json}` under `general/audits/`) |
| `fix_imports` | Rewrite-only import auto-fixer (safe import rewrites; no `__init__.py` regeneration) |
| `circular_deps` | Circular dependency scan (`circular_deps_scan_*.{md,json}` under `general/audits/`) |
| `impact_scanner` | One-shot impact scan for a target file (inbound/outbound + trees) (`impact_scan_*.{md,json}` under `general/audits/`) |
| `safe_move_planner` | Safe move orchestration (move + import rewrites + optional `regenerate_package_inits` + optional `verify_imports`) |
| `layer_dependency_graph` | Bucket adjacency graph (`layer_dependency_graph_*.md` under `general/audits/`) |
| `public_symbol_export_checker` | Public symbol vs `__init__` export surface report (`public_symbol_export_check_*.{md,json}` under `general/audits/`) |
| `unreachable_module_detector` | Unreachable module detector (reachability + orphan-cascade waves + SCC clusters) (`unreachable_module_detector_run_*.{md,json}` under `general/audits/`) |

**CI parity:** [`.github/workflows/health-check.yml`](../../../../.github/workflows/health-check.yml) runs `ci_runner --strict --fail-on-skipped` — use the same flags locally to match Actions.

**Example**

```text
cd input/kaggle-ml-comp-scripts/scripts
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --help
```

**Strict precheck (CI: fail on skip stub):** `AUDIT_MACHINE_STRICT=1` or `--strict` on `audit_precheck`.

## Thin CLI wrappers (optional)

Compatibility scripts under [`entrypoints/`](entrypoints/) add `scripts/` to `sys.path` and call the same `main()` as the `-m` modules. Prefer `python -m` for new scripts and docs.

**Workspace / artifact root** (without importing the full `level_0_infra` package, so optional `torch`/`torchvision` are not required for skip-stub paths): `layers.layer_2_devtools.level_1_impl.level_2.audit_artifact_bootstrap` loads `path/workspace.py` from disk. Full-package imports: `...level_0.path.workspace` for use inside an environment where devtools inits are safe.

**Setup (Windows):** [setup/setup_project_venv.ps1](setup/setup_project_venv.ps1) — venv and `requirements-dev.txt` at the `kaggle-ml-comp-scripts` package root.

The legacy `scripts/dev/README.md` points here.
