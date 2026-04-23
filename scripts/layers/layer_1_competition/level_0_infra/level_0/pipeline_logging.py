"""Log :class:`PipelineResult` for contest CLI handlers."""

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import PipelineResult

_logger = get_logger(__name__)


def log_result(result: PipelineResult) -> None:
    if result.success:
        _logger.info("✅ %s succeeded", result.stage)
        if result.artifacts:
            _logger.info("  artifacts=%s", dict(result.artifacts))
        if result.metadata:
            _logger.info("  metadata=%s", dict(result.metadata))
        return
    _logger.error("❌ %s failed", result.stage)
    if result.error:
        _logger.error("  error=%s", result.error)
    if result.metadata:
        _logger.error("  metadata=%s", dict(result.metadata))