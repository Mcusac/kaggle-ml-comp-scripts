"""ARC-AGI-2 run folder + metadata helpers.

All run-tracking logic is intentionally implemented inside the ARC contest package
to allow fast iteration before any cross-contest abstractions are introduced.
"""

import os
import platform
import shutil
import sys
import time

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger, is_kaggle

from layers.layer_1_competition.level_0_infra.level_0 import (
    ensure_run_dir, 
    read_json, 
    write_json,
    ContestRunPathsProtocol,
    contest_run_dir, 
    contest_runs_root,
    )

logger = get_logger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_stage_slug(stage: str) -> str:
    raw = (stage or "").strip().lower()
    return "".join(ch if (ch.isalnum() or ch in ("+", "_", "-")) else "_" for ch in raw) or "unknown"


def generate_run_id(stage: str, seed: int) -> str:
    """Generate a sortable run id. Includes stage + seed for quick scanning."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{ts}_{_safe_stage_slug(stage)}_seed{int(seed)}"


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


def _merge_dict(dst: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Shallow+recursive merge for dict values only."""
    out = dict(dst)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


def _try_get_gpu_name() -> Optional[str]:
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except Exception:
        return None
    return None


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


def init_run_context(
    *,
    stage: str,
    data_root: str,
    seed: int,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    argv: Optional[list[str]] = None,
    paths: Optional[ContestRunPathsProtocol] = None,
) -> RunContext:
    """Create run folder and write initial `run_metadata.json` (status=running).

    ``paths`` optionally overrides output base for run folders (defaults to ``ARC26Paths()``).
    """
    sid = run_id.strip() if run_id else ""
    if not sid:
        sid = generate_run_id(stage=stage, seed=seed)
    resolved_dir = resolve_run_dir(run_id=sid, run_dir=run_dir, paths=paths)
    ensure_run_dir(resolved_dir, subdirs=("artifacts", "logs"))

    started_utc = _utc_now_iso()
    start_time = time.time()
    argv_list = list(argv) if argv is not None else list(sys.argv)

    ctx = RunContext(
        run_id=sid,
        run_dir=resolved_dir,
        stage=str(stage),
        seed=int(seed),
        data_root=str(data_root),
        argv=argv_list,
        started_utc=started_utc,
        start_time=start_time,
    )

    arc_paths = ARC26Paths()
    payload: dict[str, Any] = {
        "schema_version": 1,
        "contest": "arc_agi_2",
        "run_id": ctx.run_id,
        "timestamp_utc": started_utc,
        "stage": str(stage),
        "status": "running",
        "commands": {
            "argv": ctx.argv,
            "raw": " ".join(ctx.argv),
        },
        "inputs": {
            "data_root": str(data_root),
            "dataset_files": {
                "training_challenges": arc_paths.training_challenges_path().name,
                "evaluation_challenges": arc_paths.evaluation_challenges_path().name,
                "test_challenges": arc_paths.test_challenges_path().name,
            },
        },
        "repro": {
            "seed": int(seed),
            "determinism_notes": "seed set via framework set_seed(args.seed)",
        },
        "runtime": {
            "is_kaggle": bool(is_kaggle()),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "device": None,
            "gpu_name": None,
            "duration_sec": None,
        },
        "artifacts": {
            "run_dir": str(ctx.run_dir),
        },
        "metrics": {
            "offline": None,
            "kaggle": {"submission_id": None, "public_lb": None},
        },
        "notes": {"measured": [], "observed": [], "hypotheses": []},
    }

    # Best-effort runtime device capture (non-fatal)
    gpu_name = _try_get_gpu_name()
    if gpu_name:
        payload["runtime"]["device"] = "cuda"
        payload["runtime"]["gpu_name"] = gpu_name
    else:
        payload["runtime"]["device"] = os.environ.get("KAGGLE_ACCELERATOR_TYPE") or "cpu"

    write_json(ctx.manifest_path, payload)
    ctx.commands_path.write_text(payload["commands"]["raw"] + "\n", encoding="utf-8")
    logger.info("Initialized ARC run folder: %s", ctx.run_dir)
    return ctx


def update_run_metadata(run: RunContext, patch: dict[str, Any]) -> None:
    """Merge a patch into `run_metadata.json`."""
    current = read_json(run.manifest_path) if run.manifest_path.exists() else {}
    merged = _merge_dict(current, patch)
    write_json(run.manifest_path, merged)


def finalize_run_success(run: RunContext) -> None:
    duration = max(0.0, time.time() - float(run.start_time))
    update_run_metadata(
        run,
        {
            "status": "success",
            "runtime": {"duration_sec": duration},
        },
    )


def finalize_run_failure(run: RunContext, error: Exception) -> None:
    duration = max(0.0, time.time() - float(run.start_time))
    update_run_metadata(
        run,
        {
            "status": "failed",
            "runtime": {"duration_sec": duration},
            "errors": [repr(error)],
        },
    )


def copy_artifact_into_run(run: RunContext, *, src: Path, dest_name: str) -> Path:
    """Copy a file into `run_dir/artifacts/<dest_name>` and record it."""
    dest = run.artifacts_dir / dest_name
    ensure_dir(dest.parent)
    shutil.copy2(src, dest)
    update_run_metadata(run, {"artifacts": {dest_name: str(dest.relative_to(run.run_dir))}})
    return dest

