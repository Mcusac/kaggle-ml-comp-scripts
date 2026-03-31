"""Adapter implementing ``ContestPipelineProtocol`` for ARC path-based stages."""

from pathlib import Path
from typing import Any, Optional

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (
    run_submission_pipeline,
    run_train_pipeline,
    run_tune_pipeline,
)


class ArcContestPipeline:
    """Thin wrapper mapping protocol method names to ``run_*`` stage functions."""

    def train_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]:
        train_mode = str(kwargs.get("train_mode", "end_to_end"))
        models = kwargs.get("models") or ["baseline_approx"]
        if isinstance(models, str):
            models = [m.strip() for m in models.split(",") if m.strip()]
        max_targets = int(kwargs.get("max_targets", 0) or 0)
        return run_train_pipeline(
            data_root=data_root,
            train_mode=train_mode,
            models=list(models),
            run_ctx=kwargs.get("run_ctx"),
            max_targets=max_targets,
        )

    def submit_pipeline(self, data_root: str, strategy: str, **kwargs: Any) -> Path:
        raw_models = kwargs.get("models")
        models: Optional[list[str]] = None
        if isinstance(raw_models, str):
            models = [m.strip() for m in raw_models.split(",") if m.strip()]
        elif isinstance(raw_models, list):
            models = [str(m) for m in raw_models]
        return run_submission_pipeline(
            data_root=data_root,
            strategy=strategy,
            output_json=kwargs.get("output_json") or kwargs.get("output_csv"),
            max_targets=int(kwargs.get("max_targets", 0) or 0),
            run_ctx=kwargs.get("run_ctx"),
            tuned_config_path=kwargs.get("tuned_config_path") or kwargs.get("tuned_config"),
            train_metadata_json=kwargs.get("train_metadata_json"),
            models=models,
            neural_checkpoint_path=kwargs.get("neural_checkpoint_path"),
            neural_train_config_path=kwargs.get("neural_train_config_path"),
            train_mode=str(kwargs.get("train_mode", "end_to_end")),
        )

    def tune_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]:
        model_name = str(kwargs.get("model_name", kwargs.get("model", "baseline_approx")))
        search_type = str(kwargs.get("search_type", "quick"))
        max_targets = int(kwargs.get("max_targets", 0) or 0)
        return run_tune_pipeline(
            data_root=data_root,
            model_name=model_name,
            search_type=search_type,
            max_targets=max_targets,
            run_ctx=kwargs.get("run_ctx"),
        )
