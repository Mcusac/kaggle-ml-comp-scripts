"""ARC-AGI-2 run initialization; generic run types live in competition infra."""

import os
import platform
import sys
import time

from pathlib import Path
from typing import Any, Optional

from layers.layer_0_core.level_0 import ensure_dir, get_logger, is_kaggle
from layers.layer_0_core.level_4 import save_json

from layers.layer_1_competition.level_0_infra.level_1 import RunContext
from layers.layer_1_competition.level_0_infra.level_0 import (
    generate_run_id,
    utc_now_iso,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.paths import ARC26Paths
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.run import resolve_run_dir

_logger = get_logger(__name__)


def _try_get_gpu_name() -> Optional[str]:
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except Exception:
        return None
    return None


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

    gpu_name = _try_get_gpu_name()
    if gpu_name:
        payload["runtime"]["device"] = "cuda"
        payload["runtime"]["gpu_name"] = gpu_name
    else:
        payload["runtime"]["device"] = os.environ.get("KAGGLE_ACCELERATOR_TYPE") or "cpu"

    save_json(payload, ctx.manifest_path)
    ctx.commands_path.write_text(payload["commands"]["raw"] + "\n", encoding="utf-8")
    _logger.info("Initialized ARC run folder: %s", ctx.run_dir)
    return ctx