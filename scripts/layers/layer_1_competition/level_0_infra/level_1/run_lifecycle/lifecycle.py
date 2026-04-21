"""Merge patches into run metadata and finalize run folders."""

import shutil
import time

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import ensure_dir
from layers.layer_0_core.level_4 import load_json_raw, save_json

from .run_context import RunContext


def _merge_dict(dst: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    """Shallow+recursive merge for dict values only."""
    out = dict(dst)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dict(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


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