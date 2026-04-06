## `.cursor/` policy (kaggle-ml-comp-scripts)

This folder contains **repo/package-specific** Cursor artifacts for
`input/kaggle-ml-comp-scripts/`.

- **Repo-specific rules live in**: `input/kaggle-ml-comp-scripts/.cursor/rules/`
- **Rule scopes** should be kept narrow via `globs` so they only apply to:
  - `input/kaggle-ml-comp-scripts/scripts/**/*.py`, or
  - `input/kaggle-ml-comp-scripts/scripts/**/__init__.py` (for init/export rules)

### What belongs here

- Architecture and layering rules for `scripts/layers/**`
- Import surface discipline for this package
- `__init__.py` export standards and fail-fast import rules

### What does not belong here

- Cross-repo operational tooling rules for workspace-wide `.cursor/audit-results`,
  agent templates, or commands. Those should live in the workspace root
  `.cursor/`.
