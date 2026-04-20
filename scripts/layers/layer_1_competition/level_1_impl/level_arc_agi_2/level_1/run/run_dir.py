"""Run directory resolution helpers for ARC-AGI-2."""

from pathlib import Path
from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestRunPathsProtocol
from layers.layer_1_competition.level_0_infra.level_1 import contest_run_dir, contest_runs_root

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import ARC26Paths


def default_runs_root(paths: Optional[ContestRunPathsProtocol] = None) -> Path:
    """Return `/kaggle/working/arc_agi_2/runs` (or local output mirror)."""
    base_paths = paths if paths is not None else ARC26Paths()
    return contest_runs_root(base_paths, "arc_agi_2")


def resolve_run_dir(
    run_id: str,
    run_dir: Optional[str] = None,
    paths: Optional[ContestRunPathsProtocol] = None,
) -> Path:
    """Resolve run directory from explicit path or `(runs_root / run_id)`."""
    if run_dir and str(run_dir).strip():
        return Path(str(run_dir)).expanduser().resolve()
    base_paths = paths if paths is not None else ARC26Paths()
    return contest_run_dir(base_paths, "arc_agi_2", str(run_id))
