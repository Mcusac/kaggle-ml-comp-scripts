"""Copy a submission artifact into a run folder and finalize metadata."""

from pathlib import Path
from typing import Any

from .lifecycle import (
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    update_run_metadata,
)
from .run_context import RunContext


def commit_run_artifacts(
    run_ctx: RunContext,
    patch: dict[str, Any],
    *,
    src_path: Path,
    dest_name: str,
) -> None:
    """Merge ``patch`` into run metadata, copy ``src_path`` into the run
    artifacts directory as ``dest_name``, and finalize the run.

    On any exception in the three sub-steps, finalize the run as failed with
    the caught exception (preserves the broad ``except Exception`` shape the
    previous inline call sites used).
    """
    try:
        update_run_metadata(run_ctx, patch)
        copy_artifact_into_run(run_ctx, src=src_path, dest_name=dest_name)
        finalize_run_success(run_ctx)
    except Exception as e:
        finalize_run_failure(run_ctx, e)