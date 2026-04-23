# Code-audit: reusable Task prompt slots

**Orchestrator speed:** For comprehensive runs, prefer **`Task(code-audit-runner)`**
→ `run_code_audit_pipeline` (see **Runner** block below and **Step 1f** in
`.cursor/agents/code-audit-orchestrator-details.md`), then drive precheck + planner +
auditor from each queue JSON row’s `level_path`, `level_name`, and `audit_scope` — do
not re-type the full target list in chat. **Default `artifact_policy: regenerate`**
(**Step 0.7** in orchestrator-details): always run 3a+3b per target and overwrite canonical inventory/audit
files unless `USER_REQUEST` explicitly requests **incremental_only**.

**Default `run_mode: recommendations-only`** (**Step 1c** in orchestrator-details): documentation-first unless
the user asked to **apply fixes** / **active overhaul** / **`run_mode default`**.

**Step 0.8:** Do **not** use `comprehensive_audit_emit.py` instead of real
`code-audit-planner` + `code-audit-auditor` unless the user opted into **machine emit only**
/ **use emit script** / **skeleton inventory only**.

**Preferred:** The **main assistant** uses the **Main assistant (orchestrator) preamble** below, then **`Task(subagent_type="code-audit-planner", …)`** and **`Task(subagent_type="code-audit-auditor", …)`** with the Planner and Auditor blocks. **Legacy:** the preamble may be pasted into **`Task(subagent_type="code-audit", …)`** only if nested planner/auditor Tasks work in your environment; otherwise use the preferred pattern (see Step 0.8 in `.cursor/agents/code-audit-orchestrator-details.md`). **Always** embed the user’s full message as a quoted **`USER_REQUEST`** block (see `.cursor/rules/code-audit-delegation.mdc`). Replace `{placeholders}` before sending.

**Canonical specs**

- Orchestrator entry + **Step 3**: `.cursor/agents/code-audit.md`
- Orchestrator policy / machine steps / Step 4 / guardrails: `.cursor/agents/code-audit-orchestrator-details.md`
- Discovery / Step 1e / handoff: `.cursor/agents/code-audit-reference.md`
- Planner: `.cursor/agents/code-audit-planner.md`
- Auditor: `.cursor/agents/code-audit-auditor.md`
- Machine pipeline (queue + manifest): `.cursor/agents/code-audit-runner.md`
- Manifest triage (read-only, inline JSON): `.cursor/agents/code-audit-analyzer.md`
- Post-fix / CI manifest regression check: `.cursor/agents/code-verify-runner.md`

**Machine queue (comprehensive) — preferred**

Delegate **`Task(subagent_type="code-audit-runner", …)`** with the **Runner** block below
(not ad-hoc `shell` + `audit_targets.py` for the same handoff).

**Legacy (devtools only)**

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_targets --write-manifest "{path_to_audit_queue.json}"
```

**Precheck (per target; cwd = `scripts/`)**

```bash
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope {audit_scope} --level-path "{level_path}" --level-name "{level_name}"
```

Optional: `--precheck-kind contest_tier|contest_root|special_tree` for
`contests_special` when auto-detection is insufficient. JSON rows from
`audit_targets.py` include `precheck_kind` for reference.

---

## Main assistant (orchestrator) preamble

Use this **in the main chat assistant** before delegating **Planner** then **Auditor** `Task`s (canonical Step 3). The same preface may be wrapped in **`Task(subagent_type="code-audit", …)`** only as **legacy** when nested `Task` calls are supported.

```
USER_REQUEST (verbatim):

```
{USER_REQUEST}
```

Workspace root: {workspace_root}

Read `.cursor/agents/code-audit-orchestrator-details.md` in full, then run the
pipeline: Step 0 (normalize), Step 0.5 (`audit_profile` / `audit_preset`), Step 0.6 (precheck mode),
Step 1f optional (**`Task(code-audit-runner)`** / `run_code_audit_pipeline` for comprehensive),
Step 2.7 (`audit_precheck.py` per target unless skip/pin), Step 3a → 3b per
target per `.cursor/agents/code-audit.md` (**invoke `code-audit-planner` then `code-audit-auditor`**
— typically via `Task` from this assistant, not simulated in-process). Read `.cursor/agents/code-audit-reference.md` in full for Step 1e and
handoff integrity.

Optional: target queue file (absolute): {target_json_path}
```

---

## Runner (`code-audit-runner`) — machine pipeline only

Use for **Step 1f** (comprehensive queue + versioned manifest). The runner returns paths only;
it does not perform Step 3. Embed **`USER_REQUEST`** if the Task policy requires it.

**Queue + manifest for main orchestration** (you will still run **Step 2.7** and **Step 3** per target):

```text
Delegate Task(subagent_type="code-audit-runner") with:

Working directory for the command: kaggle-ml-comp-scripts/scripts/

Run:
python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline --no-precheck --no-general-scan --no-csiro-scan --workspace-root "{artifact_base}" --run-id "{run_id}"

(Adjust: add --output-dir or --manifest if pinning paths; --date YYYY-MM-DD; --no-queue-file if manifest-only.)
```

**Full machine pass** (precheck + general stack + CSIRO inside the pipeline — only when `USER_REQUEST` asks for machine-only / CI / all machine steps): **omit** `--no-precheck`, `--no-general-scan`, and `--no-csiro-scan`.

Follow `.cursor/agents/code-audit-runner.md`. Return only: `manifest_path`, `queue_path`, `exit_code`, `overall_exit_code` (structured block).

---

## Analyzer (`code-audit-analyzer`) — manifest only

Use **after** `code-audit-runner` (or when you already have a v1 `manifest.json`). The analyzer
**does not** run tools, **does not** read `audit_queue.json` or paths under `md_path` / `json_path` inside the manifest.

**Paste manifest in Task (preferred for small files):**

```text
Delegate Task(subagent_type="code-audit-analyzer") with:

USER_REQUEST (optional, verbatim):
"""
{USER_REQUEST}
"""

Manifest JSON (full body of schema_version 1 from run_code_audit_pipeline):
"""
{manifest_json}
"""
```

**Or single file path (read only that file):**

```text
Delegate Task(subagent_type="code-audit-analyzer") with:

manifest_path (absolute, single file to read):
{manifest_path}
```

Follow `.cursor/agents/code-audit-analyzer.md`. Output: structured findings (Run, By layer, By step, Not applicable) — no extra repo I/O.

---

## Verify runner (`code-verify-runner`) — baseline manifest regression

Use **after** a fix or to gate a second machine pass against a **known-good** (or pre-fix) v1
`manifest.json`. Re-runs **`run_code_audit_pipeline`** with **flag parity** to the baseline
run; writes a **new** manifest under a **new** `--run-id` (or `--output-dir`).

**Paste Task:**

```text
Delegate Task(subagent_type="code-verify-runner") with:

baseline_manifest_path (absolute, v1 manifest.json from the reference run):
{baseline_manifest_path}

verify_run_id (new, must not overwrite baseline):
{verify_run_id}

Parity: same flags as the baseline run, e.g.:
python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline --no-precheck --no-general-scan --no-csiro-scan --workspace-root "{artifact_base}" --run-id "{verify_run_id}"
(Replace with the exact flag line used for the baseline; add --date, --strict, etc. if those were used.)

```

Follow `.cursor/agents/code-verify-runner.md`. Return: `baseline_manifest_path`, `new_manifest_path`, `verdict`, `regression`, deltas — no planning, no source edits.

---

## Planner (`code-audit-planner`)

```
level_name: {level_name}
level_path (absolute): {level_path}
audit_scope: {audit_scope}
audit_profile: {audit_profile}
generated: {generated}
pass_number: {pass_number}
run_id: {run_id}

precheck_report_path (absolute, optional): {precheck_report_path}
inventory_bootstrap_path (optional): {inventory_bootstrap_path}

Write the inventory to:
.cursor/audit-results/{audit_scope}/inventories/INVENTORY_{level_name}.md

Follow `.cursor/agents/code-audit-planner.md`.
```

---

## Auditor (`code-audit-auditor`)

```
level_name: {level_name}
level_number: {level_number}
level_path (absolute): {level_path}
audit_scope: {audit_scope}
audit_profile: {audit_profile}
audit_preset: {audit_preset}
generated: {generated}
pass_number: {pass_number}
run_id: {run_id}
run_mode: {run_mode}

Inventory (absolute path to INVENTORY_{level_name}.md): {inventory_path}

prior_level_apis (labeled blocks === PRIOR: <level_name> ===):
{prior_level_apis}

precheck_report_path (absolute, optional): {precheck_report_path}

Persist audit to:
.cursor/audit-results/{audit_scope}/audits/{level_name}_audit.md

Follow `.cursor/agents/code-audit-auditor.md`.
```
