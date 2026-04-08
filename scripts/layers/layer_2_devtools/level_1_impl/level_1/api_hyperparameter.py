"""Public API: hyperparameter analyze / verify CLIs."""

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.hyperparameter_workflow_ops import (
    run_analyze_hyperparameters as _run_analyze_hyperparameters,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.hyperparameter_workflow_ops import (
    run_verify_hyperparameter_recommendations as _run_verify_hyperparameter_recommendations,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok


def run_analyze_hyperparameters_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Run hyperparameter grid analysis workflow.

    Config: ``model_type``, optional ``metadata_dir``, ``top_n``, ``top_percentile``,
        ``expansion_factor``, ``output_path``, ``as_json``.
    """
    try:
        mt = config.get("model_type")
        if mt is None:
            return err(["model_type is required"])
        rc = _run_analyze_hyperparameters(
            model_type=str(mt),
            metadata_dir=Path(config["metadata_dir"]).resolve()
            if config.get("metadata_dir")
            else None,
            top_n=int(config.get("top_n", 20)),
            top_percentile=float(config.get("top_percentile", 0.1)),
            expansion_factor=float(config.get("expansion_factor", 1.2)),
            output_path=Path(config["output_path"]).resolve()
            if config.get("output_path")
            else None,
            as_json=bool(config.get("as_json", False)),
        )
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def run_verify_hyperparameter_recommendations_cli_api(
    config: dict[str, Any],
) -> dict[str, Any]:
    """Verify recommendations JSON against metadata."""
    try:
        mt = config.get("model_type")
        rec = config.get("recommendations_path")
        if mt is None or rec is None:
            return err(["model_type and recommendations_path are required"])
        rc = _run_verify_hyperparameter_recommendations(
            model_type=str(mt),
            recommendations_path=Path(rec).resolve(),
            metadata_dir=Path(config["metadata_dir"]).resolve()
            if config.get("metadata_dir")
            else None,
            as_json=bool(config.get("as_json", False)),
        )
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


__all__ = [
    "run_analyze_hyperparameters_cli_api",
    "run_verify_hyperparameter_recommendations_cli_api",
]
