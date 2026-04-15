# CLI

CLI argument parsing and command dispatch.

## Purpose

Universal arguments, model-type/path/ensemble argument groups, and command dispatch with primary and fallback handlers.

## Contents

- `common_args.py` – add_common_arguments
- `argument_groups.py` – add_model_type_argument, add_model_path_argument, add_ensemble_method_argument
- `dispatcher.py` – dispatch_command
- `commands.py` – Command enum
- `args_utils.py` – get_arg, parse_comma_separated, comma_separated_type, parse_key_value_pairs

## Public API

- `add_common_arguments` – Add --config arg to parser
- `add_model_type_argument`, `add_model_path_argument`, `add_ensemble_method_argument` – Argument group helpers
- `dispatch_command` – Dispatch to handler by command name
- `Command` – Enum of valid framework commands (TRAIN, TEST, etc.)
- `get_arg`, `parse_comma_separated`, `comma_separated_type`, `parse_key_value_pairs` – Argument parsing utilities

## Dependencies

stdlib only (argparse, enum, typing).

## Usage Example

```python
from layers.layer_0_core.level_0 import add_common_arguments, add_model_type_argument, dispatch_command

parser = argparse.ArgumentParser()
add_common_arguments(parser)
add_model_type_argument(parser, model_type_choices=["vision", "tabular"])
dispatch_command(args.command, args, primary_handlers={"train": train_handler})
```
