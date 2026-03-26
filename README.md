# ML Competition Framework

A unified, reusable machine learning competition framework supporting both computer vision and tabular tasks.

## Features

- **Domain-Specific**: Separate packages for vision and tabular ML
- **Contest Abstraction**: Easily adapt to new competitions
- **SOLID Architecture**: Clean, maintainable, extensible code
- **Full Pipeline Support**: Grid search, ensembling, cross-validation
- **Production Ready**: Checkpointing, progress tracking, error handling

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt

# Install package (from project root)
pip install -e scripts/
# Or: cd scripts && pip install -e .
```

## Structure

```
kaggle-ml-comp-scripts/
├── scripts/           # Framework code
│   ├── config/        # Configuration system
│   ├── contest/       # Contest abstraction
│   ├── vision/        # Computer vision domain
│   ├── tabular/       # Tabular ML domain
│   ├── pipelines/     # Orchestration pipelines
│   ├── utils/         # Cross-cutting utilities
│   ├── cli/           # Command-line interface
│   ├── dev/           # Development tools
│   └── templates/     # Project templates
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Usage

**Run the CLI:**

- From project root: `python scripts/run.py train --contest csiro --model efficientnet_b0 ...`
- From `scripts/`: `python run.py train --contest csiro --model efficientnet_b0 ...`

## Kaggle and local testing

**Adding this dataset in a Kaggle notebook**

1. Create a Kaggle dataset by dragging the **kaggle-ml-comp-scripts** folder (or this repo) into [Kaggle Datasets](https://www.kaggle.com/datasets). In the notebook, add that dataset and the competition dataset (e.g. csiro-biomass) as inputs.
2. Install and path:

   ```python
   import sys
   sys.path.insert(0, '/kaggle/input/kaggle-ml-comp-scripts/scripts')
   # Optionally: !pip install -r /kaggle/input/kaggle-ml-comp-scripts/requirements.txt
   ```

3. Run commands: `!python /kaggle/input/kaggle-ml-comp-scripts/scripts/run.py train --contest csiro --model efficientnet_b0 --data-root /kaggle/input/csiro-biomass` or import and call the pipelines.

**Local mimic (test pathing before Kaggle)**

Use `input/` and `working/` to mirror Kaggle:

| Local        | Kaggle                    |
| ------------ | ------------------------- |
| `input/`     | `/kaggle/input/`          |
| `working/`   | `/kaggle/working/`        |
| `input/kaggle-ml-comp-scripts/` | `/kaggle/input/kaggle-ml-comp-scripts/` |
| `input/csiro-biomass/`    | `/kaggle/input/csiro-biomass/`    |

- Put the notebook in `working/` and run from there.
- Put the kaggle-ml-comp-scripts folder under `input/kaggle-ml-comp-scripts/`, and competition data under `input/<competition-slug>/`.
- `contest.paths.local_data_root` resolves to `input/<competition-slug>` in this layout when not on Kaggle.

## Status

- **Vision**: models (timm, DINOv2), data loading, training, inference, TTA, metrics.
- **Tabular**: models (logistic, ridge, xgboost, lgbm, mlp), training, inference, threshold optimization.
- **Pipelines**: atomic (train, predict, evaluate, export), workflows (train_predict, cross_validate, train_and_export), grid search, ensembling.
- **CLI**: train, test, train_test, grid_search, cross_validate, ensemble, export. Contests: CSIRO, CAFA.
- **Dev tools**: check_health, cleanup_imports, check_health_thresholds.
- **Partial**: CSIRO dataset_manipulation, advanced workflows (dataset_grid_search, submit_best). **regression_ensemble** is implemented and wired in CLI. Use `pip install -r requirements.txt` for full deps; `pip install -e scripts/` uses setup.py core deps.

## Known Gaps

- CSIRO biomass-specific streaming/aggregation: use `vision.data` or a small contest shim.
- Advanced CSIRO pipelines: dataset_grid_search, submit_best, etc. not yet wired in CLI.

## Documentation

### Contest Reference Guides

- **CAFA_FUNCTIONALITY_CATALOG.md** - Complete catalog of all CAFA functionality (detailed reference)
- **CAFA_REFERENCE.md** - Lessons learned and gap analysis for CAFA implementation
- **CSIRO_REFERENCE.md** - Comprehensive functionality catalog, lessons learned, and gap analysis for CSIRO
- **CSIRO_QUICK_REFERENCE.md** - Quick status lookup for CSIRO implementation

### Framework Guides

- **NOTEBOOK_GUIDE.md** - Guide for notebook usage, contest selection, and cell roles

## Design Principles

- **DRY**: Shared infrastructure eliminates duplication
- **SOLID**: Clear interfaces, single responsibility
- **YAGNI**: No unnecessary abstractions
- **KISS**: Simple, straightforward implementations

## License

MIT License - See LICENSE file for details
