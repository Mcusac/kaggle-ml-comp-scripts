# level_1/cli

## Purpose
CLI subparser setup and command builders for grid search, ensemble, submission, train-export, and regression ensemble.

## Contents
- `subparsers.py` — `setup_framework_subparsers`: add model type, path, ensemble method arguments
- `builders/` — Command builders: `GridSearchCommandBuilder`, `RegressionEnsembleCommandBuilder`, `StackingCommandBuilder`, `SubmissionCommandBuilder`, `TrainExportCommandBuilder`, `EnsembleCommandBuilder`

## Public API
- `setup_framework_subparsers(subparsers, model_type_choices, ensemble_methods)` → None
- `builders.*` — All command builder classes and ensemble weight utilities

## Dependencies
- `level_0` — `add_common_arguments`, `add_model_type_argument`, `add_model_path_argument`, `add_ensemble_method_argument`, `BaseCommandBuilder`

## Usage Example
```python
from level_1.cli import setup_framework_subparsers
from level_1.cli.builders import GridSearchCommandBuilder

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()
setup_framework_subparsers(subparsers, model_type_choices=["vision", "tabular"], ensemble_methods=["average"])
```
