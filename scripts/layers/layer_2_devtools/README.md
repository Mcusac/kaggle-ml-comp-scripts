# Devtools (`layer_2_devtools`)

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
| `inventory_bootstrap` | Planner merge fragment |
| `validate_before_upload` | Pre-upload checks |
| `check_health` / `check_health_thresholds` | Health reports |

**CI parity:** [`.github/workflows/health-check.yml`](../../../../.github/workflows/health-check.yml) runs `run_code_audit_pipeline` with `--strict --fail-on-skipped` before `check_health` and `check_health_thresholds --strict` — use the same flags locally to match Actions.

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
