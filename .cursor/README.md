## `.cursor/` policy (kaggle-ml-comp-scripts)

This folder contains **repo/package-specific** Cursor artifacts for
`input/kaggle-ml-comp-scripts/`.

- **Repo-specific rules live in**: `input/kaggle-ml-comp-scripts/.cursor/rules/`
- **Repo-local slash command docs (audit passes)**: `input/kaggle-ml-comp-scripts/.cursor/commands/` — **copy-paste recipes:** `code-audit-quick-reference.md`; hub: `audit-pass.md`; targets: `audit-targets.md`; tags: `audit-pass-tags.md`
- **Rule scopes** should be kept narrow via `globs` so they only apply to:
  - `input/kaggle-ml-comp-scripts/scripts/**/*.py`, or
  - `input/kaggle-ml-comp-scripts/scripts/**/__init__.py` (for init/export rules)

### What belongs here

- Architecture and layering rules for `scripts/layers/**`
- Import surface discipline for this package
- `__init__.py` export standards and fail-fast import rules

### Workspace vs repo `.cursor/`

- **Workspace root** `.cursor/` holds shared agents, global commands (e.g. `/code-audit`), and pointers for cross-repo tooling. **`kaggle-ml-comp-scripts` audit deliverables** (inventories, audits, prechecks, manifests) live under **`input/kaggle-ml-comp-scripts/.cursor/audit-results/`** — see [audit-results/README.md](audit-results/README.md). Devtools index: [scripts/layers/layer_2_devtools/README.md](../scripts/layers/layer_2_devtools/README.md) (see also [scripts/dev/README.md](../scripts/dev/README.md) for a short redirect).
- **This repo** may still host **package-scoped** command markdown under `.cursor/commands/` so audit workflows stay next to `scripts/layers/**` rules (Cursor discovers commands per project configuration).
