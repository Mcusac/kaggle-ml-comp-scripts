# Notebook infra

- `build_run_py_base_command` — shared argv prefix for `python run.py --contest <name> <subcommand> --data-root ...`; contest `notebook_commands` extend this list.
- `path_bootstrap.bootstrap_notebook_environment` — after the notebook inserts `scripts/` on `sys.path`, call this to run `prepend_framework_paths` and optional `KAGGLE_COMP_CONTEST`.
- `bootstrap_notebook` (this package) — thin wrapper around `bootstrap_notebook_environment` for callers that already import `layers`.
- `run_cli_streaming` — run a command list with live output; returns exit code and last N lines.
- `get_notebook_commands_module` — lazy-import contest `notebook_commands` (registered per contest in `registration.py`).

Contest-specific builders live under `level_1_impl/level_<name>/level_0/notebook_commands.py`.
