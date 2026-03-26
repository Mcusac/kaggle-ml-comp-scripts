# Layer 2 devtools

Kaggle competition repo tooling: package health scans, audit precheck, import probes, hyperparameter helpers, and maintenance CLIs.

## Packages

| Package | Role |
|--------|------|
| **`layer_0_infra`** | Reusable primitives and small compositions: paths, AST/JSON parse, scanners, format helpers, reporters. |
| **`level_1_impl`** | Composed workflows (`level_0.composed`) and stable entry APIs (`level_1.api_*`), plus executable scripts in `level_2`. |

Import examples:

```python
from layers.layer_2_devtools.level_0_infra.level_0 import FormattingHelpers
from layers.layer_2_devtools.level_0_infra.level_1 import SectionFormatters
from layers.layer_2_devtools.level_1_impl.level_1.api_audit import resolve_workspace
```

## Tests

From the `scripts` directory (with `scripts` on `PYTHONPATH`, e.g. via `path_bootstrap`):

```text
python -m pytest layers/layer_2_devtools/level_1_impl/tests -q
```

## Further detail

See [level_0_infra/README.md](level_0_infra/README.md) for infra tier boundaries (`level_0` → `level_1` → `level_2`).
