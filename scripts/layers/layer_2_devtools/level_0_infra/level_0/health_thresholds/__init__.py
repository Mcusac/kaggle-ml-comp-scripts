"""Health metric threshold configuration (limits only).

Runtime threshold *checking* against analysis dicts lives in ``level_0_infra.level_1.checker``.
"""

from .config import ThresholdConfig

__all__ = ["ThresholdConfig"]
