# level_1/runtime/config

## Purpose
Configuration creation and section formatting for training, grid search, and evaluation. Integrates with level_0 schemas.

## Contents
- `config_creation.py` — `create_config`, `format_config_section`, `log_config_section`, `print_config_section`
- `config_sections.py` — section formatting helpers
- `training.py` — `TrainingConfig`
- `grid_search.py` — `GridSearchConfig`
- `evaluation.py` — `EvaluationConfig`

## Public API
- `create_config(...)` — build config from args and schemas
- `format_config_section(section_name, config)` → formatted string
- `log_config_section(logger, section_name, config)`
- `print_config_section(section_name, config)`
- `TrainingConfig` — training section dataclass
- `GridSearchConfig` — grid search section dataclass
- `EvaluationConfig` — evaluation section dataclass

## Dependencies
- `level_0` — `get_arg`, `ConfigValidationError`, `RuntimeConfig`, `TrainingSchema`, `EvaluationSchema`

## Usage Example
```python
from level_1.runtime.config import create_config, TrainingConfig, print_config_section

config = create_config(args, runtime_config, training_schema)
print_config_section("training", config)
```
