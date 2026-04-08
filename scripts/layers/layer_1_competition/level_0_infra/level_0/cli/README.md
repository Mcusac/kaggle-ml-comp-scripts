## Purpose

Shared argparse subparser wiring helpers for the competition CLI entrypoints.

## Contents

| Module | Description |
|--------|-------------|
| `parser_helpers` | Adds contest subcommands and common flags to an argparse subparser tree |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.cli`:

- **add_grid_search_parsers**
- **add_training_parsers**
- **add_ensemble_parsers**
- **add_submission_parsers**

## Dependencies

- Stdlib only (`typing`)

## Usage Example

```python
import argparse

from layers.layer_1_competition.level_0_infra.level_0.cli import add_training_parsers

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", required=True)

def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--contest", required=True)

add_training_parsers(subparsers, _add_common)
```
