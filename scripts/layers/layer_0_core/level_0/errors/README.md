# Errors

Exception hierarchy for framework-level failures.

## Purpose

Domain-specific exception types for clearer error handling and debugging. Each base class has subclasses for specific failure modes.

## Contents

- `config_errors.py` – ConfigError, ConfigValidationError, ConfigLoadError
- `data_errors.py` – DataError, DataLoadError, DataValidationError, DataProcessingError
- `model_errors.py` – ModelError, ModelLoadError, ModelTrainingError, ModelPredictionError
- `pipeline_errors.py` – PipelineError, PipelineSetupError, PipelineExecutionError
- `runtime_errors.py` – CoreRuntimeError, DeviceError, EnvironmentConfigError, ProcessError, ExecutionError

## Public API

All exception classes. Use base classes for broad except blocks; subclasses for specific handling.

## Dependencies

stdlib only.

## Usage Example

```python
from level_0 import DataLoadError, DeviceError, ConfigValidationError

try:
    df = load_csv(path)
except FileNotFoundError as e:
    raise DataLoadError(f"Failed to load {path}: {e}") from e
```
