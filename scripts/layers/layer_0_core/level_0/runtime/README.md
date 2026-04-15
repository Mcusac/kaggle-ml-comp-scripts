# Runtime

Environment detection, logging, torch availability, cache paths, and subprocess execution.

## Purpose

Detects Kaggle vs local environment, configures logging, provides lazy torch import, derives cache directory paths, builds subprocess command lists, and streams command output.

## Contents

- `platform_detection.py` – `is_kaggle`, `is_kaggle_input`
- `log_configure.py` – `setup_logging`, `get_logger`, `reset_logging`, `get_isolated_logger`
- `torch_guard.py` – `get_torch`, `is_torch_available`
- `cache_paths.py` – `DerivedCachePaths`, `derive_cache_paths`
- `execution_result.py` – `ExecutionResult` dataclass
- `runtime_types.py` – `ProcessResult`, `DeviceInfo` TypedDicts
- `base_command_builder.py` – `BaseCommandBuilder`
- `run_command_stream.py` – `run_command_stream`

## Public API

- `is_kaggle` – True if running in a Kaggle kernel (env-based)
- `is_kaggle_input` – True if a path string is under `/kaggle/input` (path-prefix heuristic)
- `setup_logging` – Configure root logger with handlers and level
- `get_logger` – Get a named logger
- `reset_logging` – Remove all handlers from the root logger
- `get_isolated_logger` – Get a logger isolated from the root handler chain
- `get_torch` – Lazy torch module import (returns None if unavailable)
- `is_torch_available` – Bool check for torch availability
- `DerivedCachePaths` – Dataclass of resolved cache directory paths
- `derive_cache_paths` – Derive `DerivedCachePaths` from a base directory
- `ProcessResult` – TypedDict for subprocess returncode, stdout, stderr
- `DeviceInfo` – TypedDict for CUDA availability and device names
- `BaseCommandBuilder` – Base class for building subprocess command lists
- `ExecutionResult` – Dataclass for executed operation result (returncode, output, log_file)
- `run_command_stream` – Execute command and stream output, returns (returncode, last_n_lines)

## Dependencies

stdlib (subprocess, collections, os, logging, dataclasses, typing). Optional: torch.

## Usage Example

```python
from layers.layer_0_core.level_0 import is_kaggle, setup_logging, run_command_stream

setup_logging(level="INFO")
returncode, lines = run_command_stream(["python", "train.py"], keep_last_n=100)
```
