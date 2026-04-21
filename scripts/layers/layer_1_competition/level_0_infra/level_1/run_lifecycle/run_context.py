"""Run folder dataclass for contest run metadata and artifacts."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunContext:
    run_id: str
    run_dir: Path
    stage: str
    seed: int
    data_root: str
    argv: list[str]
    started_utc: str
    start_time: float

    @property
    def artifacts_dir(self) -> Path:
        return self.run_dir / "artifacts"

    @property
    def logs_dir(self) -> Path:
        return self.run_dir / "logs"

    @property
    def manifest_path(self) -> Path:
        return self.run_dir / "run_metadata.json"

    @property
    def commands_path(self) -> Path:
        return self.run_dir / "commands.txt"