"""Metric registry."""

from typing import Dict, Optional

from level_0 import get_logger, Metric

logger = get_logger(__name__)


class MetricRegistry:
    """Registry for managing available metrics."""

    def __init__(self):
        self._metrics: Dict[str, Metric] = {}

    def register(self, metric: Metric) -> None:
        if metric.name in self._metrics:
            logger.warning("Metric '%s' already registered, overwriting", metric.name)
        self._metrics[metric.name] = metric
        logger.debug("Registered metric: %s", metric.name)

    def get(self, name: str) -> Optional[Metric]:
        return self._metrics.get(name)

    def list_metrics(self) -> list:
        return list(self._metrics.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._metrics

    def __repr__(self) -> str:
        return f"MetricRegistry(metrics={list(self._metrics.keys())})"


_global_registry = MetricRegistry()


def register_metric(metric: Metric) -> None:
    _global_registry.register(metric)


def get_metric(name: str) -> Optional[Metric]:
    return _global_registry.get(name)


def list_metrics() -> list:
    return _global_registry.list_metrics()
