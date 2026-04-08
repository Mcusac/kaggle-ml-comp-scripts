# infra/level_0/abstractions — Contest protocols

**On disk:** `…/level_0_infra/level_0/abstractions/`. **Import:** `layers.layer_1_competition.level_0_infra.level_0` (protocols are part of the `infra level_0` barrel).

## Purpose

Protocol definitions for contest pipelines (`ContestPipelineProtocol`, `ContestInputValidator`, `ContestMetric`). Contest code under `level_1_impl/level_<name>/` implements these; import paths use `layers.layer_1_competition.level_1_impl.<contest>` per project rules.

## Contents

| Module | Description |
|--------|-------------|
| `contest_abstractions` | ContestPipelineProtocol, ContestInputValidator, ContestMetric |

## Public API

- **ContestPipelineProtocol** — Protocol for train_pipeline, submit_pipeline, tune_pipeline
- **ContestInputValidator** — Protocol for validate_inputs
- **ContestMetric** — Protocol for compute(y_pred, y_true, config, **kwargs)

## Dependencies

- None (stdlib only: pathlib, typing)

## Usage Example

```python
from pathlib import Path
from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestPipelineProtocol

class MyContestPipeline(ContestPipelineProtocol):
    def train_pipeline(self, data_root: str, **kwargs) -> Optional[Path]:
        raise NotImplementedError

    def submit_pipeline(self, data_root: str, strategy: str, **kwargs) -> Path:
        raise NotImplementedError

    def tune_pipeline(self, data_root: str, **kwargs) -> Optional[Path]:
        raise NotImplementedError
```
