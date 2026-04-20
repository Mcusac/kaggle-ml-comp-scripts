"""ARC-AGI-2 RunContext + run-metadata lifecycle helpers.

Holds the dataclass + the four lifecycle ops (init, update, success, failure)
plus the artifact-copy helper. Run-id and run-dir resolution live in sibling
modules (`run_id.py`, `run_dir.py`) to keep this file SRP-focused on the
per-run lifecycle.
"""

import os
import platform
import shutil
import sys
import time

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger, is_kaggle
from layers.layer_0_core.level_4 import load_json_raw, save_json

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ARC26Paths,
    utc_now_iso,
    generate_run_id,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import resolve_run_dir

logger = get_logger(__name__)


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
    paths: Optional[Any] = None,
) -> RunContext:
    """Create run folder and write initial `run_metadata.json` (status=running).

    ``paths`` optionally overrides output base for run folders (defaults to ``ARC26Paths()``).
    """
    sid = run_id.strip() if run_id else ""
    if not sid:
        sid = generate_run_id(stage=stage, seed=seed)
    resolved_dir = resolve_run_dir(run_id=sid, run_dir=run_dir, paths=paths)
    ensure_dir(resolved_dir)
    ensure_dir(resolved_dir / "artifacts")
    ensure_dir(resolved_dir / "logs")

    started_utc = utc_now_iso()
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

    save_json(payload, ctx.manifest_path)
    ctx.commands_path.write_text(payload["commands"]["raw"] + "\n", encoding="utf-8")
    logger.info("Initialized ARC run folder: %s", ctx.run_dir)
    return ctx


def update_run_metadata(run: RunContext, patch: dict[str, Any]) -> None:
    """Merge a patch into `run_metadata.json`."""
    current = load_json_raw(run.manifest_path) if run.manifest_path.exists() else {}
    merged = _merge_dict(current, patch)
    save_json(merged, run.manifest_path)


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
