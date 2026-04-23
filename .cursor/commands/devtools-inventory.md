# devtools-inventory

**Purpose:** quick copy-paste for `layer_2_devtools` so orchestrators and subagents run existing tools and read artifacts instead of re-implementing checks.

**Authoritative checklists and mapping:** [automation_ideas.md](../../docs/automation_ideas.md). **Module table:** [layer_2_devtools README](../../scripts/layers/layer_2_devtools/README.md).

**Shell:** `cd` to `input/kaggle-ml-comp-scripts/scripts` (one line; no `&&` in PowerShell 5.x). Windows users: see [kaggle-ml-scripts.mdc](../../../.cursor/rules/kaggle-ml-scripts.mdc) for `artifact_base` and audit layout.

---

## Most-used entrypoints (cwd: `…/kaggle-ml-comp-scripts/scripts`)

**Machine pipeline (CI parity):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline --help
```

Example (local parity with `health-check` workflow, from `scripts/`, `artifact_base` = parent `kaggle-ml-comp-scripts`):

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline --workspace-root ".." --strict --fail-on-skipped
```

**General stack import-layer scan (writes under `../.cursor/audit-results/general/audits/` by default):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.scan_level_violations --json
```

Strict exit when any violation (local gate; `artifact_base` JSON includes `suggested_min_level` where applicable):

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.scan_level_violations --json --fail-on-violations
```

**Barrel enforcement (general + CSIRO contest + competition infra, merged `barrel_enforcement_scan.v1`):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.scan_barrel_enforcement --json
```

Optional draft move checklist (no file moves; reads the same scan payload):

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.scan_level_violations --emit-move-plan
```

**Layer dependency report** — *different scope:* bucket graph for `layer_2_devtools` + `dev`, not a full rescan of `layer_0_core` (use `scan_level_violations` for that). Paths printed on success:

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_layer_dependencies
```

**Apply fixes from latest `level_violations_scan_*.json` (default dry-run; use `--apply` to write):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.apply_violation_fixes --help
```

**Package health (JSON for thresholds / cleanup):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root .. --json
```

**Strict thresholds (after `check_health` wrote `../health_report.json` at repo root):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health_thresholds ../health_report.json --strict
```

**Remove unused imports (needs health JSON from `check_health`):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.cleanup_imports --report ../health_report.json --dry-run
```

**Deterministic `__init__.py` regen (pass your tree as `--root`):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.regenerate_package_inits --root PATH_TO_PACKAGE_TREE --dry-run
```

**Import verification and import test suite:**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.verify_imports
python -m layers.layer_2_devtools.level_1_impl.level_2.test_imports
```

**Planner fragment / precheck (orchestrated workflows):**

```text
python -m layers.layer_2_devtools.level_1_impl.level_2.inventory_bootstrap
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --help
```

---

## Chat orchestration (not `python -m`)

- **Audit:** `/code-audit` — see [code-audit-quick-reference.md](code-audit-quick-reference.md)
- **Fix (tool-first):** `/code-fix` — see workspace `/.cursor/commands/code-fix.md` and `.cursor/rules/code-fix-delegation.mdc`

## Related rules

- `input/kaggle-ml-comp-scripts/.cursor/rules/devtools-automation-usage.mdc` — do not re-scan when a devtool already exists
- `input/kaggle-ml-comp-scripts/.cursor/rules/python-import-surfaces.mdc` — barrel and path policy

This command will be available in chat with /devtools-inventory
