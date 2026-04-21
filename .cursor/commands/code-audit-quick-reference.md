# code-audit quick reference

**Copy-paste recipes** for `/code-audit`, **main-agent orchestration** (`Task(code-audit-planner)` / `Task(code-audit-auditor)` per target), **`Task(code-audit-runner)`** for `run_code_audit_pipeline` (Step 1f), optional **`Task(code-audit-analyzer)`** to summarize a v1 machine **manifest** (inline fields only; no sidecar reads), and legacy **`Task(code-audit)`** on this repo.  
Authoritative policy: workspace `.cursor/agents/code-audit-orchestrator-details.md`, `.cursor/agents/code-audit-reference.md`, `.cursor/rules/code-audit-delegation.mdc`.

**Related:** [audit-pass.md](audit-pass.md) (focused passes) · [audit-targets.md](audit-targets.md) (`@` paths) · [audit-pass-tags.md](audit-pass-tags.md) (finding tags).

**Apply phase (after audit):** [code-fix.md](code-fix.md) — tool-first fixes; summaries in `audit-results/<scope>/summaries/` as `FIX_RUN_*.md`.

---

## How to invoke

1. Chat: type **`/code-audit`**, then paste **one** block from below (or merge lines). The **assistant in this chat** runs orchestration and should delegate **`code-audit-planner`** then **`code-audit-auditor`** per target (not a single nested `Task(code-audit)` for full compliance).
2. Subagents (focused): copy prompts from workspace **`.cursor/audit-templates/task-prompt-templates.md`** (Planner / Auditor / Runner / **Analyzer** blocks); embed the user’s message as a verbatim **`USER_REQUEST`** block per `code-audit-delegation.mdc`.

---

## Main agent orchestration (preferred for Step 3)

Orchestration (Steps 0–2.7, Step 4) runs in the **main assistant**. For **each** target, fill placeholders and run **in order**:

1. **`Task(subagent_type="code-audit-planner", …)`** — use the **Planner** block in `.cursor/audit-templates/task-prompt-templates.md` (`level_name`, `level_path`, `audit_scope`, `precheck_report_path`, …).
2. **`Task(subagent_type="code-audit-auditor", …)`** — use the **Auditor** block (`inventory_path`, `prior_level_apis`, `run_mode`, …).

Pass the user’s **`USER_REQUEST`** (and workspace root) in your orchestration preamble so targets and `@` paths stay verbatim. **Step 1f:** **`Task(subagent_type="code-audit-runner", …)`** for `run_code_audit_pipeline` — see **Runner** block in workspace **`.cursor/audit-templates/task-prompt-templates.md`** and **`.cursor/agents/code-audit-runner.md`**. **Optional:** **`Task(subagent_type="code-audit-analyzer", …)`** to turn **manifest.json** (v1) into layer-grouped findings (manifest-only; no queue/sidecar reads) — see **`.cursor/agents/code-audit-analyzer.md`**. Optional **`Task(subagent_type="shell", …)`** only for commands that are **not** the unified pipeline; return paths to the **main** agent, not under a nested `Task(code-audit)`.

---

## Subagent `Task` templates (copy-paste)

Replace placeholders: **`<TARGET>`** = full `@` path to a tree under `scripts/layers/...` (see sections below for examples). Keep **`@`** on its own token; do not paraphrase inside the `"""` block.

### `code-audit` — legacy (avoid for full planner/auditor compliance)

A single **`Task(code-audit)`** may not be able to spawn nested planner/auditor Tasks. Prefer **`/code-audit`** in chat or **Main agent orchestration** above.

```text
Delegate Task(subagent_type="code-audit") with:

USER_REQUEST (verbatim):

"""
profile full
recommendations only
no code edits

@<TARGET>
"""
```

### `code-fix` — apply after an audit (same `<TARGET>`)

```text
Delegate Task(subagent_type="code-fix") with:

USER_REQUEST (verbatim):

"""
apply recommendations
profile full

@<TARGET>
"""
```

### `code-fix` — lite (tools only; edit the tools line)

```text
Delegate Task(subagent_type="code-fix") with:

USER_REQUEST (verbatim):

"""
tools: init regen

@<TARGET>
"""
```

### Two-phase: audit then fix (same `<TARGET>`)

Run **`/code-audit`** (or main-agent orchestration with planner/auditor Tasks) **first**; when it finishes, run **`/code-fix`** or **`Task(code-fix)`** (or paste both into one chat that runs them **sequentially**).

```text
/code-audit
profile full
recommendations only
no code edits

@<TARGET>
```

```text
Delegate Task(subagent_type="code-fix") with:

USER_REQUEST (verbatim):

"""
apply recommendations
profile full

@<TARGET>
"""
```

**Rules:** `.cursor/rules/code-audit-delegation.mdc` · `.cursor/rules/code-fix-delegation.mdc`

---

**Defaults (if you omit them):**

- **`profile`:** `full`
- **`run_mode`:** findings-only (`recommendations-only`) — no repo edits unless you add **`apply fixes`** / **`active overhaul`** / **`run_mode default`**

**Artifact layout:**

- `.cursor/audit-results/<scope>/inventories/INVENTORY_<level_name>.md`
- `.cursor/audit-results/<scope>/audits/<level_name>_audit.md`
- `.cursor/audit-results/<scope>/summaries/` (precheck, journals, manifests)

**Scopes:** `general` (layer_0_core), `competition_infra` (level_0_infra tiers), `contests_special` (typically under `contests/`; use `@` paths for `level_1_impl`).

---

## Knobs (optional lines)

Add any of these inside your request:

| Intent | Lines to add |
|--------|----------------|
| Import-only pass | `profile imports` |
| Barrel / `__init__` surfaces | `profile barrels` |
| README pass | `profile docs` |
| Force findings-only | `recommendations only` / `no code edits` |
| Allow edits | `apply fixes` / `active overhaul` |
| Skip machine precheck | `skip precheck` |
| Pin precheck report | `precheck path: <absolute-or-workspace path to precheck_*.md>` |
| Pin precheck date | `precheck date YYYY-MM-DD` |
| Incremental / skip replan | phrases in Step 0.7 of orchestrator-details (e.g. `incremental only`) |

---

## Follow-up: apply fixes (`/code-fix`)

After **`/code-audit`** on a tree, run **`/code-fix`** with the same `@` path to apply **tool-first** changes (e.g. init regeneration) and record a **`FIX_RUN_<date>.md`** under `.cursor/audit-results/<scope>/summaries/`.

```text
/code-fix
apply recommendations
profile full

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_arc_agi_2
```

**Lite** (you choose tools): e.g. add `tools: init regen` in your request (see `code-fix.md`).

---

## Competition infrastructure (`competition_infra`)

Path base: `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra`

### All infra tiers (recommended wording)

```text
/code-audit
audit competition infra
profile full
recommendations only
no code edits

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra
```

The orchestrator discovers `level_0`, `level_1`, … under that tree and runs **precheck → planner → auditor** per tier in ascending order.

### Single tier (explicit token)

```text
/code-audit
audit level_0_infra/level_2
profile full
recommendations only
```

Replace `level_2` with `level_0`, `level_1`, etc.

Legacy alias example: `audit level_C2` → same as `level_0_infra/level_2`.

### Import / dependency sanity only

```text
/code-audit
audit competition infra
profile imports
recommendations only

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra
```

### Avoid this pattern

- **`audit level_0_infra`** alone — **not** a documented token; prefer **`audit competition infra`** or **`audit level_0_infra/level_N`**.
- Jumbled spacing: keep **`@`** as its own token (`… infra` then newline or space then `@…`).

---

## Implementation layer (`level_1_impl`)

No standard phrase like “audit all impl”; pin the tree with **`@`**:

### Whole impl tree

```text
/code-audit
profile full
recommendations only
no code edits

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl
```

### One contest package under impl

```text
/code-audit
profile full
recommendations only

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_csiro
```

---

## General stack (`layer_0_core`, `audit_scope: general`)

### All numeric levels under core

```text
/code-audit
audit all general levels
profile full
recommendations only
no code edits
```

### Single level

```text
/code-audit
audit level_5
profile full
recommendations only
```

**Note:** bare `audit level_N` refers to **`layer_0_core/level_N`**, not competition infra.

---

## Comprehensive multi-segment (long run)

```text
/code-audit
comprehensive audit all scopes
profile full
recommendations only
```

Uses the full segment queue (general → competition_infra → contests → …). Prefer manifest from `python -m layers.layer_2_devtools.level_1_impl.level_2.audit_targets` (cwd `kaggle-ml-comp-scripts/scripts/`) when driving subagents (see workspace `/code-audit` command).

---

## Subagent wrapper — legacy `Task(code-audit)` (competition infra example)

Prefer chat **`/code-audit`** with the same `USER_REQUEST` for planner/auditor compliance. If you still use a single subagent:

```text
Delegate Task(subagent_type="code-audit") with:

USER_REQUEST (verbatim):

"""
audit competition infra
profile full
recommendations only

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra
"""
```

Paste your block **inside** the `"""` … no paraphrasing; keep every `@` path.

---

## Parallel chats

Safe pattern for **findings-only**: open three chats, each **`/code-audit`** + one of:

- competition infra block (above)
- `level_1_impl` `@` block
- `audit all general levels` block

Avoid parallel **`apply fixes`** across trees that share churn on the same imports unless coordinated.

---

## Windows shell (precheck / scripts)

From repo scripts root:

```text
cd "input/kaggle-ml-comp-scripts/scripts"
```

one command per line; do not use `&&` in PowerShell 5.x.

This file is for humans; slash name in Cursor may vary. Bookmark or open in editor for copy-paste.
