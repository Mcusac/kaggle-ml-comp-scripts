"""Public API: deterministic code-audit machine pipeline (thin re-export).

Implementation lives in ``level_2.pipeline_ops`` so callers that import only this module
avoid loading the full ``level_1`` package ``__init__`` (e.g. lightweight manifest runs).
"""

from __future__ import annotations

from layers.layer_2_devtools.level_1_impl.level_2.pipeline_ops import run_code_audit_pipeline

__all__ = ["run_code_audit_pipeline"]
