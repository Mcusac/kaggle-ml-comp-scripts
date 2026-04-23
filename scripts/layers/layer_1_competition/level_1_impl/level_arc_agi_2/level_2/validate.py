"""Validate-data stage (standalone ``PipelineResult`` wrapper around ``validate_arc_inputs``)."""

from typing import Optional

from layers.layer_0_core.level_0 import PipelineResult, get_logger

from layers.layer_1_competition.level_0_infra.level_0 import metadata_merge
from layers.layer_1_competition.level_0_infra.level_1 import (
    RunContext,
    update_run_metadata,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    validate_arc_inputs,
)


_logger = get_logger(__name__)


def run_validate_data_pipeline(
    *,
    data_root: str,
    max_targets: int = 0,
    run_ctx: Optional[RunContext] = None,
) -> PipelineResult:
    """Validate ARC inputs (standalone pipeline stage)."""
    try:
        validate_arc_inputs(data_root=str(data_root), max_targets=int(max_targets or 0))
        if run_ctx is not None:
            update_run_metadata(
                run_ctx,
                {
                    "config": {"validate_data": {"max_targets": int(max_targets or 0)}},
                    "inputs": {"data_root": str(data_root)},
                    "validation": {"status": "success"},
                },
            )
        return PipelineResult.ok(
            stage="validate_data",
            metadata=metadata_merge({"data_root": str(data_root), "max_targets": int(max_targets or 0)}),
        )
    except Exception as e:
        if run_ctx is not None:
            try:
                update_run_metadata(
                    run_ctx,
                    {
                        "config": {"validate_data": {"max_targets": int(max_targets or 0)}},
                        "inputs": {"data_root": str(data_root)},
                        "validation": {"status": "failed", "error": repr(e)},
                    },
                )
            except (OSError, KeyError, ValueError, TypeError) as meta_err:
                _logger.warning(
                    "validate_data: failed to persist failure metadata for run=%s: %s",
                    getattr(run_ctx, "run_id", "?"),
                    meta_err,
                )
        return PipelineResult.fail(
            stage="validate_data",
            error=str(e),
            metadata=metadata_merge({"data_root": str(data_root), "max_targets": int(max_targets or 0), "error_repr": repr(e)}),
        )
