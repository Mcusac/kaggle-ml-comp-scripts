# layer_Z_unsorted

Staging area for work-in-progress that does not yet belong in a numbered `level_*` package under `layers/`.

## Policy

- **Do not add long-lived production code here.** New logic should land in the appropriate `layer_*` tree as soon as dependencies are clear.
- **Drain regularly:** move modules into `layer_0_core`, `layer_1_competition/level_0_infra`, or `layer_1_competition/level_1_impl/<contest>/level_K` and delete stubs from this folder.
- **Checklist before promoting:** identify the lowest `level_K` that can own the code; ensure imports obey that package’s layering rules; add or update `__init__.py` barrels only for the same `level_K`.
