"""Public API: deterministic code-fix machine pipeline (thin re-export).

Implementation lives in ``level_2.fix_pipeline_ops`` so callers that import only this module
avoid pulling extra imports beyond the pipeline runner.
"""

from __future__ import annotations

from layers.layer_2_devtools.level_1_impl.level_2.fix_pipeline_ops import run_code_fix_pipeline

__all__ = ["run_code_fix_pipeline"]

