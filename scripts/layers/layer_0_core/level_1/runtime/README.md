# runtime

## Purpose
Infrastructure utilities: hardware detection, environment-aware path resolution, subprocess execution, reproducibility seeding, GPU memory management, CLI command builders, and progress display configuration.

## Contents
- `base_pipeline.py` — `BasePipeline`: abstract lifecycle base (setup → execute → cleanup → run)
- `cache_paths.py` — `DerivedCachePaths`, `derive_cache_paths`: compute feature/model cache paths
- `device.py` — `get_device`, `get_device_info`, `is_cuda_available`
- `lazy_imports.py` — `lazy_import`: generic deferred importer for optional dependencies
- `metadata_paths.py` — `find_metadata_candidates`: locates model metadata JSON near a model path
- `notebook_runner.py` — `safe_execute_cell`: wraps notebook cell execution with enable/disable gate
- `paths.py` — `get_environment_type`, `get_environment_paths`, `get_environment_root`, `resolve_environment_path`, `resolve_path`
- `process.py` — `run_command`: subprocess execution returning stdout/stderr/returncode
- `progress_config.py` — `ProgressVerbosity`, `ProgressConfig`: display verbosity levels and settings dataclass
- `result_checks.py` — `validate_execution_result`: raises `ExecutionError` if a result indicates failure
- `seed.py` — `set_seed`: sets Python/numpy/torch random seeds for reproducibility
- `setup_framework_subparsers.py` — `setup_framework_subparsers`: registers train/test/ensemble/export/submit CLI subparsers
- `command_builders/` — `BaseCommandBuilder` subclasses for programmatic CLI invocation
- `config/` — `TrainingConfig`, `EvaluationConfig`, `GridSearchConfig`, `create_config`, `format_config_section`, `log_config_section`, `print_config_section`
- `cuda/` — GPU memory cleanup, usage statistics, and monitoring

## Public API
See sub-package `__init__.py` files for full symbol lists.

## Dependencies
- `level_0` — `is_kaggle`, `get_torch`, `is_torch_available`, `get_logger`, `DeviceError`, `EnvironmentConfigError`, `ExecutionError`, `ExecutionResult`, `ProcessResult`, `run_command_stream`, `BaseCommandBuilder`

## Usage Example
```python
from level_1.runtime import get_device, set_seed, ProgressConfig
device = get_device("auto")
set_seed(42)
cfg = ProgressConfig.from_env()
```