# Code-audit orchestrator — reference (not a Task subagent)

**Audience:** the `code-audit` orchestrator only. Read this file **in full** when
resolving targets, paths, comprehensive segments, and planner ↔ auditor handoff.
Parsing, precheck policy, artifact policy, machine steps, and Step 4 live in
`code-audit-orchestrator-details.md`; **Step 3** (planner/auditor delegation) lives in
`code-audit.md`.

---

## Step 1 — Determine the target levels and discovery roots

**If `audit_preset` is `comprehensive`:** skip to **Step 1e** (ignore the
single-scope bullets below for target discovery — segments replace them).

Parse the user's request (after Step 0 normalization) to determine the scope:

- **Single level** — e.g. "audit level_2" → run only `level_2` (still apply
  Step 0 dedupe/sort for consistency).
- **List of levels** — from explicit tokens or `@` paths; order is **always**
  the normalized ascending list from Step 0.
- **All general levels** — discover under
  **`input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core/`**
  (the general stack tree). List immediate child directories matching
  `level_(\d+)`, dedupe, sort by ascending **N**. **Do not** treat the vague
  “workspace root” as the discovery root for this repo.
- **All competition infra (`competition_infra` scope)** — discover under
  **`input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra/`**:
  child dirs `level_N`; emit targets with `level_name = level_N` and
  `level_path = level_0_infra/level_N` (see Step 0 item 5 and Step 1e Segment 2).
- **All levels** only when the user truly means every scope — otherwise prefer
  scoped discovery above. For contest or competition-infra sweeps, use paths they named
  or the packages listed in Step 1b.

Regardless of the order in `USER_REQUEST`, **always process** the final target
list in **ascending** order for that scope. Never audit a higher dependent
level before all **lower** targets in **this run** have completed planner +
auditor.

**Shell:** Do not instruct subagents to run Windows PowerShell 5.x one-liners
using bash-style `&&` or `||` (invalid). Use separate commands or
PowerShell-native flow (`if ($LASTEXITCODE -ne 0) { ... }`).

---

## Step 1b — Map each target to an audit scope and output folder

Use this table so inventories and audits land under
`artifact_base/.cursor/audit-results/<scope>/…` where **`artifact_base`** is
`input/kaggle-ml-comp-scripts` for targets in that tree (see
`input/kaggle-ml-comp-scripts/.cursor/audit-results/README.md`):

| Scope | Levels / packages | Base path |
|--------|-------------------|-----------|
| `general` | `level_0` … `level_10` | `.cursor/audit-results/general/` |
| `competition_infra` | `level_0` … `level_4` (one per `level_0_infra/level_N` on disk) | `.cursor/audit-results/competition_infra/` |
| `contests_special` | e.g. `level_cafa`, `level_csiro`, `level_rna3d`, `level_Z`, contest-specific trees | `.cursor/audit-results/contests_special/` |

**Valid output trees only:**

- `.cursor/audit-results/<scope>/inventories/`
- `.cursor/audit-results/<scope>/audits/`
- `.cursor/audit-results/<scope>/summaries/`

**Never** treat `.cursor/audit-results/` **without** a `scope` subfolder and
artifact type folder as the primary destination.

**File paths:**

- Planner inventory (when written to disk):
  `.cursor/audit-results/<scope>/inventories/INVENTORY_<level_name>.md`
- Auditor result:
  `.cursor/audit-results/<scope>/audits/<level_name>_audit.md`
- Consolidated summaries for that run:
  `.cursor/audit-results/<scope>/summaries/`

`<level_name>` is unique per artifact:

- General stack: `level_0` … `level_10` (directory basename under `scripts/layers/layer_0_core/`).
- Competition infra: **`level_name`** = `level_N` (matches on-disk `level_0_infra/level_N/` and
  Python import `layers.layer_1_competition.level_0_infra.level_N`). `path_bootstrap.py` prepends
  `scripts/` so `layers.*` resolves; it does **not** create junctions.
- Contest tier packages: `{contest_pkg}_level_{K}` where `contest_pkg` is the
  immediate child name under `scripts/layers/layer_1_competition/contests/` (e.g. `level_cafa`) and
  `K` is the numeric suffix of child `level_K` (e.g. `level_cafa_level_1`).
- Contest package **root** (`.py` files directly under the contest package, e.g.
  `registration.py`): `level_<contest_pkg>_root` (e.g. `level_cafa_root`).

---

## Step 1e — Comprehensive preset: build segment queue

When **`audit_preset` is `comprehensive`**, build an ordered list of **segments**.
Run segments **sequentially**. **Never** run two segments in parallel.

**Machine queue:** The same segment order and `level_name` rules are implemented in
`python -m layers.layer_2_devtools.level_1_impl.level_2.audit_targets` from `kaggle-ml-comp-scripts/scripts/` (JSON output).
Prefer running that script and iterating its `targets` array instead of
re-deriving this section from prose (see `code-audit-orchestrator-details.md` Step **1f**).

Within each segment, maintain a **fresh** `context_store` (see Step 2 in
`code-audit-orchestrator-details.md`). Do **not**
reuse `prior_level_apis` from a previous segment (general vs contest `level_2`
must not collide).

### Segment 1 — `audit_scope: general`

1. Root: `input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core/`.
2. Discover immediate child directories whose names match `level_(\d+)` with
   **N** in `0` … `10`.
3. Sort by **N** ascending.
4. For each `level_N`, emit target:
   - `level_name` = `level_N`
   - `level_path` = `{root}/level_N`
   - `level_number` = **N**

### Segment 2 — `audit_scope: competition_infra`

1. Root: `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra/`.
2. Discover immediate child directories whose names match `level_(\d+)` (on-disk
   competition infra: `level_0`, `level_1`, …). **Exclude** `__pycache__` and
   anything that is not a directory.
3. Sort by numeric **N** ascending.
4. For each directory `level_N`, emit target:
   - `level_name` = `level_N` (e.g. `level_2`) — scope folder `competition_infra/`
     keeps artifacts distinct from `general/` even when basenames match
   - `level_path` = `{root}/level_{N}` (the actual path on disk)
   - `level_number` = **N** (infra tier index for Phase 7 within `competition_infra`)

### Segment 3 — `contests_special` (one sub-segment per contest package)

1. Root: `input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/contests/`.
2. For each immediate child directory (contest package, e.g. `level_cafa`),
   **excluding** `__pycache__`:

   **A.** Fresh `context_store = {}` for this contest only.

   **B.** Discover child directories named `level_<K>` where **K** is a
   non-negative integer. Sort by **K** ascending.

   **C.** For each `level_K`, emit target:
   - `level_name` = `{contest_pkg}_level_{K}` (e.g. `level_cafa_level_0`)
   - `level_path` = `{contest_pkg_path}/level_K`
   - `level_number` = **K** (contest tier for Phase 7)

   **D.** If the contest package directory contains **any** `*.py` file
   **directly** in that directory (not in subfolders), emit **after** all
   `level_K` targets:
   - `level_name` = `{contest_pkg}_root` (e.g. `level_cafa_root`)
   - `level_path` = contest package directory
   - `level_number` = `0`

   **E.** For **each** target in order **C** then **D**, run **Step 3** (planner
   then auditor). Then move to the next contest package.

### Segment 4 — `contests_special` (`layer_Z_unsorted` and similar)

If `input/kaggle-ml-comp-scripts/scripts/layers/layer_Z_unsorted/` exists as a
directory and contains audit-relevant content, run **one** additional segment
(fresh `context_store`):

- `audit_scope` = `contests_special`
- `level_name` = `layer_Z_unsorted` (or `level_Z` if you standardize the name)
- `level_path` = that directory
- `level_number` = `0`

(Adjust if other staging packages are added under `scripts/layers/` — same
pattern: one segment per special tree outside `layer_0_core` and
`layer_1_competition`.)

After each segment (1, 2, each contest in 3, or segment 4), you may append a short
note to `.cursor/audit-results/<scope>/summaries/` listing completed
`level_name` values for that segment (optional but useful for long runs).

---

## Subagent handoff integrity (mandatory)

**Goal:** No lossy summarization between planner → auditor, between levels in
`context_store`, or when interpreting `USER_REQUEST`.

1. **Inventory → auditor (preferred):** The planner **writes**
   `INVENTORY_<level_name>.md` to the canonical path (Step 1b). Before Step 3b,
   **verify** the file exists, is non-empty, and includes `INVENTORY:` or the
   planned header for `level_name`. Pass the **absolute path** into the auditor
   prompt and instruct: **Read this file as the full inventory; do not rely on
   partial quotes in chat.**

2. **Inventory → auditor (fallback):** If the platform cannot use disk, pass
   the **full** planner return body **verbatim**. **Never** forward a shortened
   summary instead of the inventory. Truncation is a **hard failure** — use
   file-backed handoff or fail the level.

3. **`prior_level_apis`:** For each **earlier** target in **this segment**
   (lower tier / earlier in the segment list), include a block:
   `=== PRIOR: <level_name> ===` plus **PUBLIC API (post-audit)** and violation
   summaries from that target’s saved `<scope>/audits/<level_name>_audit.md` (or
   the full result if small). **Do not** drop violation lines to save tokens.
   For the general stack, `<level_name>` is still `level_0`, `level_1`, … as
   before.

4. **Large payloads:** Prefer **file-backed** references (read the path in the
   subagent) over huge inline pastes.

5. **Orchestrator must not:** Re-derive the inventory from memory, compress the
   planner output when forwarding, or call the auditor using only a
   high-level summary from a prior level instead of labeled `prior_level_apis`
   blocks.

6. **Prior artifacts on disk** do **not** complete **this** run: if
   `INVENTORY_<level_name>.md` and `<level_name>_audit.md` already exist under
   the correct scope, the orchestrator still runs Step **3a** and **3b** for
   that target and **overwrites** those files — unless `USER_REQUEST` triggers
   **`artifact_policy: incremental_only`** (see `code-audit-orchestrator-details.md` Step **0.7**).

7. **Machine emit scripts** (e.g. `comprehensive_audit_emit.py`) that template
   `INVENTORY_*` / `*_audit.md` **without** running **code-audit-planner** and
   **code-audit-auditor** are **not** equivalent to this pipeline’s handoff
   artifacts — see `code-audit-orchestrator-details.md` Step **0.8**.
