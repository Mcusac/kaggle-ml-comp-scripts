# audit-pass

**Repo-local** focused audit passes for `input/kaggle-ml-comp-scripts`. Each pass delegates to the workspace **`code-audit`** subagent (`Task(subagent_type="code-audit", …)`); do not replace that pipeline with ad-hoc reviews.

## Prerequisites (workspace root)

- Orchestrator: `.cursor/agents/code-audit.md`
- Policy / steps: `.cursor/agents/code-audit-orchestrator-details.md`, `.cursor/agents/code-audit-reference.md`
- Delegation: `.cursor/rules/code-audit-delegation.mdc` — embed the user’s full message as a verbatim **`USER_REQUEST`** block
- Prompt slots: `.cursor/audit-templates/task-prompt-templates.md`
- **Tag taxonomy:** [audit-pass-tags.md](audit-pass-tags.md)
- **Copy-paste `/code-audit` recipes (infra / impl / core):** [code-audit-quick-reference.md](code-audit-quick-reference.md)

## Pass index

| Slash doc | Purpose | Typical `audit_profile` |
|-----------|---------|-------------------------|
| [audit-pass-dependency.md](audit-pass-dependency.md) | Import direction, cycles, cross-layer | `imports` |
| [audit-pass-classify.md](audit-pass-classify.md) | Classify symbols + decomposition hints | `full` |
| [audit-pass-duplicate.md](audit-pass-duplicate.md) | DRY vs lower layers | `full` (or `imports` if narrow) |
| [audit-pass-wrappers.md](audit-pass-wrappers.md) | Thin wrappers vs intentional barrels | `barrels` |
| [audit-pass-decompose.md](audit-pass-decompose.md) | Mixed-responsibility modules | `full` |
| [audit-pass-enforce.md](audit-pass-enforce.md) | Thickness, inline IO, registry duplication | `full` |
| [audit-pass-apply.md](audit-pass-apply.md) | Same focus as enforce + **apply fixes** | `full` |
| [audit-pass-validate.md](audit-pass-validate.md) | Post-change regression check | `imports` / `full` |

**Target presets:** [audit-targets.md](audit-targets.md)

## Default behavior

- **`run_mode`:** findings-only unless the user explicitly asks to **apply fixes** (see `audit-pass-apply.md`).
- **Artifacts:** canonical paths only — `.cursor/audit-results/<scope>/{inventories,audits,summaries}/` (see `.cursor/agents/code-audit-reference.md` Step 1b).
- **Shell (Windows):** one command per line; no `&&` in PowerShell 5.x.

## Reference document convention

Use a single markdown file per campaign (e.g. multi-pass `level_0_infra` or `level_1_impl` refactor) as a **human journal**. Paths should live under the correct scope:

- `.cursor/audit-results/general/summaries/`
- `.cursor/audit-results/competition_infra/summaries/`
- `.cursor/audit-results/contests_special/summaries/`

**Contract for each pass:**

1. The `code-audit` run still produces **canonical** `INVENTORY_<level_name>.md` and `<level_name>_audit.md` for each audited target (unless `USER_REQUEST` explicitly requests incremental-only / verify-only per orchestrator Step 0.7).
2. In addition, append a short section to **`REFERENCE_DOC`** (path you supply in chat) containing:
   - pass name and date (`generated`)
   - targets audited
   - bullet findings using tags from [audit-pass-tags.md](audit-pass-tags.md)
3. Do not treat `REFERENCE_DOC` as a substitute for canonical inventory/audit files.

If `REFERENCE_DOC` does not exist, create it under the appropriate `summaries/` folder with a YAML or markdown header (`generated`, `audit_scope`, `campaign_id`).

## Composition examples

1. **Competition infra sweep:** open [audit-targets.md](audit-targets.md) → copy infra preset paths → run `/audit-pass-dependency` then `/audit-pass-classify` with those `@` paths in `USER_REQUEST`.
2. **Contest package:** use contest tier or root tokens per `code-audit-reference.md` (e.g. `audit level_csiro_level_0 profile imports`).
3. **`level_1_impl`:** use impl root from [audit-targets.md](audit-targets.md); scope is typically `contests_special` or explicit paths — follow Step 0 target normalization in `code-audit-orchestrator-details.md`.

## Verification checklist (dry run)

Use after adding commands or before a long campaign.

1. **Delegation:** Confirm the agent embeds your full message in a quoted `USER_REQUEST` block per `code-audit-delegation.mdc`.
2. **Scope folder:** After `code-audit` finishes, new or updated files exist only under `.cursor/audit-results/<scope>/{inventories,audits,summaries}/`, not flat under `.cursor/audit-results/`.
3. **Precheck:** Unless you said `skip precheck`, `precheck_<level>_<date>.md` appears under `summaries/` for the target scope when `audit_precheck.py` ran successfully.
4. **Pass intent:** `audit_profile` and findings match the pass doc you used (e.g. dependency pass → import-focused auditor Phase 7 emphasis).
5. **Findings-only:** No repo edits under `scripts/layers/` unless you invoked **audit-pass-apply** (or equivalent `apply fixes` / `run_mode default` phrasing).
6. **Reference doc:** If you named a `REFERENCE_DOC`, that file gained an appended section with dated pass header and tagged bullets.
7. **Windows:** No bash `&&` in suggested shell snippets you paste to the user.

## Global audit entry

Full multi-segment audits remain: workspace **`/code-audit`** (`.cursor/commands/code-audit.md`).

This hub doc supports `/audit-pass` discoverability when Cursor indexes repo-local commands.
