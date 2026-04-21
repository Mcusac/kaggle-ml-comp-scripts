# `artifact_base` audit results (`kaggle-ml-comp-scripts`)

**`artifact_base`** = this package root (`input/kaggle-ml-comp-scripts`), the directory that contains `scripts/` and this `.cursor/` tree.

## Layout

| Subfolder | Contents |
|-----------|----------|
| `general/` | `layer_0_core` stack (`level_0` …) |
| `competition_infra/` | `level_0_infra` tiers |
| `contests_special/` | Contests, `level_1_impl` packages, `layer_Z_unsorted`, etc. |
| `*/inventories/` | `INVENTORY_<level_name>.md` (planner output) |
| `*/audits/` | `<level_name>_audit.md` (auditor output) |
| `*/summaries/` | `precheck_*.md` / `precheck_*.json`, manifests, `FIX_RUN_*.md`, run journals |
| `*/runs/<YYYY-MM-DD>/.../` | Optional copies of precheck/snapshots |

## Machine precheck: strict mode (automation / CI)

Precheck is invoked from **`kaggle-ml-comp-scripts/scripts/`** (see [layer_2 devtools README](../../scripts/layers/layer_2_devtools/README.md)) as:

`python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck ...`

- **Default:** if optional deps (e.g. `torchvision`) are missing, a **skip stub** is still written with `precheck_status: skipped_machine_script`, and the process **exits 0** (suitable for local runs).
- **Strict:** set **`AUDIT_MACHINE_STRICT=1`** (or use **`--strict`**) so a skip stub or failed machine precheck **exits non-zero**. Use this in CI so “green” means the full stack ran, not a silent stub.
- **Schema:** JSON under `summaries/precheck_*.json` is described by `precheck_json_contract` in the devtools package; validate with  
  `python -m layers.layer_2_devtools.level_1_impl.level_2.audit_artifact_schema_check --precheck-summaries --root <artifact_base>` (add `--strict` to fail on skip stubs in those files).

## Policy pointers

- Orchestrator machine steps: workspace `.cursor/agents/code-audit-orchestrator-details.md` (Step 1f **`code-audit-runner`** / `run_code_audit_pipeline`; Step 2.7 precheck).
- Delegation: workspace `.cursor/rules/code-audit-delegation.mdc`.
- Machine pipeline agent: workspace `.cursor/agents/code-audit-runner.md`.
- Manifest triage (read-only, inline v1 JSON): workspace `.cursor/agents/code-audit-analyzer.md`.
