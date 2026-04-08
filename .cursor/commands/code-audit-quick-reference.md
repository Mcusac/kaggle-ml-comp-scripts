# code-audit quick reference

**Copy-paste recipes** for `/code-audit` and `Task(subagent_type="code-audit", …)` on this repo.  
Authoritative policy: workspace `.cursor/agents/code-audit-orchestrator-details.md`, `.cursor/agents/code-audit-reference.md`, `.cursor/rules/code-audit-delegation.mdc`.

**Related:** [audit-pass.md](audit-pass.md) (focused passes) · [audit-targets.md](audit-targets.md) (`@` paths) · [audit-pass-tags.md](audit-pass-tags.md) (finding tags).

---

## How to invoke

1. Chat: type **`/code-audit`**, then paste **one** block from below (or merge lines).
2. Subagent: wrap the **same text** as a verbatim **`USER_REQUEST`** block per `code-audit-delegation.mdc`.

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

Uses the full segment queue (general → competition_infra → contests → …). Prefer manifest from `dev/scripts/audit_targets.py` when driving subagents (see workspace `/code-audit` command).

---

## Subagent wrapper (minimal)

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
