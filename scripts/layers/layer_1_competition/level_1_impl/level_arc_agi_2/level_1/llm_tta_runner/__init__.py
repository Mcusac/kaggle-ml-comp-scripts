"""LLM-TTA DFS orchestration subpackage.

Public surface preserved: ``predict_attempts_for_llm_tta_dfs`` re-exported so
the direct-submodule import path ``...level_3.llm_tta_runner.predict_attempts_for_llm_tta_dfs``
(used by tests under ``layer_2_devtools``) continues to resolve.

Internal modules:
- ``runtime_profile`` — budget/timing/profile helpers
- ``backend_session`` — LM backend build + task-scoped cleanup
- ``decode_branches`` — three per-augmentation decode strategies
- ``artifacts`` — inference artifact layout + shard/intermediate writers
- ``ranking`` — configured ranker + fallback attempt builders
- ``runner`` — the thin orchestrator
"""

from .runner import predict_attempts_for_llm_tta_dfs

__all__ = ["predict_attempts_for_llm_tta_dfs"]
