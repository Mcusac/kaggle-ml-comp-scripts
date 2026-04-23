# code-audit

Structured audits for `input/kaggle-ml-comp-scripts`: planner inventory → auditor pass, scoped artifacts, optional comprehensive multi-segment runs.

**Copy-paste recipes (repo-local):** `input/kaggle-ml-comp-scripts/.cursor/commands/code-audit-quick-reference.md` (slash commands, main-agent orchestration + **`Task(code-audit-planner)`** / **`Task(code-audit-auditor)`**, **`Task(code-audit-runner)`** for `run_code_audit_pipeline`, optional **`Task(code-audit-analyzer)`** to triage a v1 `manifest.json` (inline only), optional **`Task(code-verify-runner)`** to re-run the pipeline and compare a new v1 manifest to a **baseline** path for regression (see **`.cursor/agents/code-verify-runner.md`**, **Verify runner** in **`.cursor/audit-templates/task-prompt-templates.md`**), legacy **`Task(code-audit)`**, and **`Task(code-fix)`** templates).

**Focused multi-pass workflows (repo-local):** `input/kaggle-ml-comp-scripts/.cursor/commands/audit-pass.md` (dependency, classify, duplicate, wrappers, decompose, enforce, apply, validate) and `audit-targets.md` for preset `@` paths.

## Two-phase workflow (review vs apply)

- **`/code-audit`** — default **`recommendations-only`**: inventories + audits; **no repo edits** unless you add apply-fix phrasing (see below). For **`__init__.py` / barrel drift**, prefer recommending the deterministic generator and follow-up **`/code-fix`** rather than line-by-line hand edits in the audit (see `code-audit-auditor.md`).
- **`/code-fix`** — optional apply phase: **tool-first** fixes (e.g. `regenerate_package_inits.py`), then minimal manual edits; writes **`FIX_RUN_*.md`** under `artifact_base/.cursor/audit-results/<scope>/summaries/`. See `.cursor/commands/code-fix.md` and `.cursor/agents/code-fix.md`.

## Default behavior (findings vs edits)

**Documentation-first:** The orchestrator **defaults** to **`run_mode: recommendations-only`** — you get inventories and audits describing **what to fix**, without the auditor applying repo edits.

**To allow applied fixes:** Add e.g. **`apply fixes`**, **`active overhaul`**, or **`run_mode default`** to your request (see `code-audit-orchestrator-details.md` Step **1c**).

## Default behavior (artifacts)

Unless the user opts into **incremental** / **verify only** / **precheck only** (see `code-audit-orchestrator-details.md` **Step 0.7**), the orchestrator runs precheck (unless skipped) + **planner + auditor** for **every** target and **overwrites** `INVENTORY_<level>.md` and `<level>_audit.md`. Existing artifacts are **not** a reason to skip Step 3.

## Fast path for agents (comprehensive)

1. Delegate **`Task(subagent_type="code-audit-runner", …)`** to run **`python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline`** from **`kaggle-ml-comp-scripts/scripts/`** once (see **Runner** block in **`.cursor/audit-templates/task-prompt-templates.md`** and **`.cursor/agents/code-audit-runner.md`**). Default outputs: manifest + `audit_queue.json` under **`artifact_base/.cursor/audit-results/general/summaries/machine_runs/<run_id>/`** unless overridden. Use **`--no-precheck --no-general-scan --no-csiro-scan`** when the main flow will still run Step 2.7 + Step 3. The orchestrator iterates the queue JSON — it does not re-list every target in chat. See **`input/kaggle-ml-comp-scripts/scripts/layers/layer_2_devtools/README.md`**.
2. Use **`.cursor/audit-templates/task-prompt-templates.md`** for planner/auditor/runner/orchestrator Task bodies (stable slots, fewer mistakes).
3. Return manifest and queue paths to the **main orchestrator** (the assistant executing `/code-audit`) — not into a nested **`Task(code-audit)`** — to save tokens. **Step 3 still runs** per target unless `USER_REQUEST` enables **incremental_only** (Step 0.7).
4. **Optional triage:** **`Task(subagent_type="code-audit-analyzer", …)`** — structured summary from **manifest body only** (see **`.cursor/agents/code-audit-analyzer.md`** and the **Analyzer** block in **`.cursor/audit-templates/task-prompt-templates.md`**). Does not replace Step 2.7/3.
5. **Optional post-fix / CI:** **`Task(subagent_type="code-verify-runner", …)`** — re-run **`run_code_audit_pipeline`**, compare the new v1 `manifest.json` to a **baseline** path (see **`.cursor/agents/code-verify-runner.md`**, **Verify runner** in **`.cursor/audit-templates/task-prompt-templates.md`**).

## Orchestrator

**Canonical:** The **main chat assistant** performs orchestration (`/code-audit` or equivalent): read the specs below, then for each target run **`Task(subagent_type="code-audit-planner", …)`** then **`Task(subagent_type="code-audit-auditor", …)`** (slots in `.cursor/audit-templates/task-prompt-templates.md`). For **Step 1f** machine queue + manifest, use **`Task(subagent_type="code-audit-runner", …)`** (not generic **`shell`** for the unified pipeline). Optional **`Task(shell, …)`** for ad-hoc commands that are not `run_code_audit_pipeline`. Hand manifest, queue path, and `precheck_report_path` back to the main agent.

**Legacy:** A single **`Task(subagent_type="code-audit", …)`** may be unable to nest planner/auditor Tasks; see `.cursor/rules/code-audit-delegation.mdc` and **Step 0.8** in orchestrator-details. Prefer the canonical pattern for spec-compliant Step 3.

The orchestrator (main assistant or legacy subagent) follows:

- `.cursor/agents/code-audit.md` — orchestrator entry: reading order, sequence summary, **Step 3** (planner/auditor delegation) in full
- `.cursor/agents/code-audit-orchestrator-details.md` — **Step 0.7** (artifacts), **Step 0.8** (planner+auditor required; no emit-script substitute), **Step 1c** (default `recommendations-only`), **Step 1f** (machine queue), **Step 0.6** / **Step 2.7** (`audit_precheck.py`; `contests_special` uses `--precheck-kind auto`), Step 4 rollup, guardrails
- `.cursor/agents/code-audit-reference.md` — Step 1 / 1b / 1e discovery, handoff integrity (read in full with the orchestrator)
- `.cursor/audit-templates/task-prompt-templates.md` — reusable prompt slots for subagents
- `.cursor/rules/code-audit-delegation.mdc` — embed the user message as a verbatim **`USER_REQUEST`** block; do not paraphrase away `@` paths or level names

Policy source of truth:

- **Delegation contract**: `.cursor/rules/code-audit-delegation.mdc`
- **Runtime sequencing/policies**: `.cursor/agents/code-audit-orchestrator-details.md`
- If wording differs in this command page vs those files, follow the rule/agent files.

Canonical write locations for this package (see `input/kaggle-ml-comp-scripts/.cursor/audit-results/README.md`); paths are under **`artifact_base/.cursor/audit-results/`** where **`artifact_base`** = `input/kaggle-ml-comp-scripts`:

- `.../inventories/INVENTORY_<level>.md`
- `.../audits/<level>_audit.md`
- `.../summaries/` (and optional `runs/<YYYY-MM-DD>/<level_name>/` snapshots from machine scripts)

Scopes: **`general`** (`layer_0_core/level_N`), **`competition_infra`** (`layer_1_competition/level_0_infra/level_N`), **`contests_special`** (per contest under `contests/`).

Package policy the auditor applies lives under `input/kaggle-ml-comp-scripts/.cursor/rules/` (`architecture.mdc`, `python-import-surfaces.mdc`, `python-import-order.mdc`, `coding-standards.mdc`, `init-exports.mdc`, etc.).

## Target queue (Step 1e, comprehensive)

Deterministic discovery is implemented in devtools (`audit_targets`; mirrors `.cursor/agents/code-audit-reference.md` Step 1e). **Canonical for orchestration:** **`Task(code-audit-runner)`** / `run_code_audit_pipeline` (Step 1f). Emit JSON for the orchestrator or delegate the runner; legacy `audit_targets` invocations:

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_targets
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_targets --markdown
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_targets --write-manifest "../.cursor/audit-results/general/summaries/audit_queue_comprehensive.json"
```

Each target in the JSON includes `precheck_kind` (`general_level`, `infra`, `contest_tier`, `contest_root`, `special_tree`). For `audit_precheck.py`, **`--precheck-kind auto`** (default) infers contest tier vs contest package root vs `layer_Z_unsorted`; override only when needed.

**Rollup skeleton** (after audits; optional):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_rollup --queue "../.cursor/audit-results/general/summaries/audit_queue_comprehensive.json" -o "../.cursor/audit-results/general/summaries/AUDIT_ROLLUP_SKELETON.md"
```

## Machine precheck and inventory bootstrap (from `scripts/`)

Orchestrator Step 2.7 and `.cursor/audit-results/README.md` describe the flow. Examples:

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope general --level-path "layers/layer_0_core/level_1" --level-name level_1
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope competition_infra --level-path "layers/layer_1_competition/level_0_infra/level_0" --level-name level_0
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope contests_special --level-path "layers/layer_1_competition/contests/level_csiro/level_0" --level-name level_csiro_level_0
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope contests_special --level-path "layers/layer_1_competition/contests/level_cafa" --level-name level_cafa_root
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope contests_special --level-path "layers/layer_Z_unsorted" --level-name layer_Z_unsorted
python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope general --full-general-scan --level-name general_stack
```

Contest roots and `layer_Z_unsorted` use **`--precheck-kind auto`** by default (no extra flags). To force a mode: `--precheck-kind contest_root` or `special_tree` or `contest_tier`.

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.inventory_bootstrap --level-path "layers/layer_0_core/level_1" --output /tmp/bootstrap_fragment.md
```

General stack-wide JSON (legacy path under `general/audits/`):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.scan_level_violations --json
```

## Example requests (paste into chat)

- Single general tier: `audit level_3 profile full` (defaults to **findings only** — no applied edits)
- Import-focused: `audit level_2 profile imports`
- Competition infra: `audit level_0_infra/level_1` or legacy alias `audit level_C1`
- Full multi-scope sweep (long run): `comprehensive audit all scopes profile full`
- **Apply fixes in-repo:** add **`apply fixes`** or **`active overhaul`** or **`run_mode default`**
- **Explicit findings-only** (redundant with default): **`recommendations only`** / **`no code edits`** / **`report-only`**
- Skip machine precheck: add **`skip precheck`** or **`no precheck`**
- Use a fixed precheck report: paste path to **`precheck_*.md`** or **`precheck path: ...`**
- Pin output date for `audit_precheck.py`: **`precheck date YYYY-MM-DD`**

## Complement: automated checks before Kaggle upload

Audits enforce architecture and surface quality; run these in addition.

**Pre-upload validation** (must run with `scripts/` as cwd so `layers.*` resolves):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload
```

**Health check** (project root; `--root` points at the package tree):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root "."
```

**pytest** (from `scripts/`):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
pytest
```

See also slash commands **`/health-check`** and **`/testing`** for full options.

This command will be available in chat with /code-audit
