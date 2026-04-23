# testing

Comprehensive testing and validation commands for the kaggle-ml-comp-scripts package.

**Package root in examples:** `input/kaggle-ml-comp-scripts`. **Commands that import `layers.*`:** run with cwd `input/kaggle-ml-comp-scripts/scripts/`.

## Prerequisites

Install dev dependencies (includes pytest). From the kaggle-ml-comp-scripts root:

- `pip install -r requirements-dev.txt`

**Important:** Most commands expect cwd **`scripts/`** so `import layers` resolves.

## Primary testing: pytest

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
pytest
pytest -v
pytest --cov=. --cov-report=html
pytest layers/layer_2_devtools/level_1_impl/tests/unit/test_config/test_base_config.py
pytest layers/layer_2_devtools/level_1_impl/tests/unit/test_contest/
pytest --cov=. --cov-report=term-missing
```

`pytest.ini` lives at `input/kaggle-ml-comp-scripts/scripts/pytest.ini` and sets `testpaths` to `layers/layer_2_devtools/level_1_impl/tests`.

## Import testing

**test_imports** (devtools API-driven):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.test_imports
python -m layers.layer_2_devtools.level_1_impl.level_2.test_imports --verbose
```

**verify_imports** (resolution probe; cwd must be the `scripts/` directory that contains `layers/`):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.verify_imports
```

**Contest import smoke tests:**

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
pytest layers/layer_2_devtools/level_1_impl/tests/unit/test_contest/test_imports_smoke.py -v
```

## Pre-upload validation

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload --verbose
```

**Health check** (optional before upload): see [health-check.md](health-check.md) (`python -m ...check_health`).

## Test layout

Pytest collection target:

```text
scripts/layers/layer_2_devtools/level_1_impl/tests/
├── unit/
├── integration/
└── ...
```

## Recommended workflows

**Before Kaggle upload:**

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload
pytest layers/layer_2_devtools/level_1_impl/tests/unit/test_contest/test_imports_smoke.py -v
```

**With coverage:**

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
pytest --cov=. --cov-report=html
```

## Common issues

- **Import errors:** Use cwd `.../kaggle-ml-comp-scripts/scripts/`.
- **Test discovery:** See `scripts/pytest.ini` and `testpaths`.
- **Coverage:** `htmlcov/index.html` after `pytest --cov=...`.

This command is available in chat with `/testing`.
