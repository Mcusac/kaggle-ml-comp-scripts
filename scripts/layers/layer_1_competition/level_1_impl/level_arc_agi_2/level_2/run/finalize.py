"""Run-artifact commit helper.

Consolidates the ``update_run_metadata`` + ``copy_artifact_into_run`` +
``finalize_run_success``/``finalize_run_failure`` try/except idiom that
``level_5/stages/{train,tune,submit}.py`` all repeat verbatim. Callers still
build their own rich ``patch`` dict (shape differs per stage); only the
boilerplate around the three lifecycle calls collapses here.
"""

from pathlib import Path
from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    RunContext,
    copy_artifact_into_run,
    finalize_run_failure,
    finalize_run_success,
    update_run_metadata,
)


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
