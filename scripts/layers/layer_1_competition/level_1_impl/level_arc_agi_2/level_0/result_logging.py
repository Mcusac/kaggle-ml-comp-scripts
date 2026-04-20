"""Shared ``_log_result`` helper for all ARC CLI handlers."""

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import PipelineResult

logger = get_logger(__name__)


def log_result(result: PipelineResult) -> None:
    if result.success:
        logger.info("✅ %s succeeded", result.stage)
        if result.artifacts:
            logger.info("  artifacts=%s", dict(result.artifacts))
        if result.metadata:
            logger.info("  metadata=%s", dict(result.metadata))
        return
    logger.error("❌ %s failed", result.stage)
    if result.error:
        logger.error("  error=%s", result.error)
    if result.metadata:
        logger.error("  metadata=%s", dict(result.metadata))
