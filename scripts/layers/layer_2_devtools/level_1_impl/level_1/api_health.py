"""Public API: package health, summaries, threshold checks, report view lines."""

import json
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.package_health_workflow_ops import (
    HealthSummaryOptions,
    run_health_summary,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.health_threshold_enforcement_ops import (
    run_health_threshold_check,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.package_health_workflow_ops import (
    PackageHealthRunOptions,
    run_package_health_cli,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok
from layers.layer_2_devtools.level_0_infra.level_0.format.health_report_views import (
    DEFAULT_COMPLEXITY_TARGET_NAMES,
    lines_complexity_targets,
    lines_duplication_summary,
    lines_health_compare,
    lines_srp_summary,
)
from layers.layer_2_devtools.level_0_infra.level_0.health_thresholds import ThresholdConfig
from layers.layer_2_devtools.level_0_infra.level_0.parse.json.report_json import load_json_report


def _threshold_config_from_optional_path(path: Path | None) -> ThresholdConfig:
    config = ThresholdConfig()
    if path and path.is_file():
        with open(path, encoding="utf-8") as f:
            config = ThresholdConfig.from_dict(json.load(f))
    return config


def run_package_health_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Run full package health; return final report text.

    Config: ``root`` (required), ``as_json`` (bool), ``threshold_config_path`` (optional Path),
    ``no_complexity``, ``no_duplication``, ``no_solid``, ``no_dead_code`` (bool).
    """
    try:
        root = config.get("root")
        if root is None:
            return err(["root is required"])
        root_p = Path(root)
        if not root_p.is_dir():
            return err([f"root is not a directory: {root_p}"])
        tc_path = Path(config["threshold_config_path"]) if config.get("threshold_config_path") else None
        threshold = _threshold_config_from_optional_path(tc_path)
        opts = PackageHealthRunOptions(
            root=root_p,
            config=threshold,
            no_complexity=bool(config.get("no_complexity", False)),
            no_duplication=bool(config.get("no_duplication", False)),
            no_solid=bool(config.get("no_solid", False)),
            no_dead_code=bool(config.get("no_dead_code", False)),
            as_json=bool(config.get("as_json", False)),
        )
        report = run_package_health_cli(opts)
        return ok({"report": report})
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return err([str(exc)])


def run_health_summary_api(config: dict[str, Any]) -> dict[str, Any]:
    """Run health JSON generation + in-process summary sections.

    Config: ``root``, ``output_json``, optional ``previous``, ``threshold_config_path``,
    ``skip_duplication``, ``skip_solid``, ``skip_dead_code``.
    """
    try:
        root = config.get("root")
        out = config.get("output_json")
        if root is None or out is None:
            return err(["root and output_json are required"])
        prev = Path(config["previous"]) if config.get("previous") else None
        tc_path = Path(config["threshold_config_path"]) if config.get("threshold_config_path") else None
        threshold = _threshold_config_from_optional_path(tc_path)
        opts = HealthSummaryOptions(
            root=Path(root),
            output_json=Path(out).resolve(),
            previous=prev,
            config=threshold,
            skip_duplication=bool(config.get("skip_duplication", False)),
            skip_solid=bool(config.get("skip_solid", False)),
            skip_dead_code=bool(config.get("skip_dead_code", False)),
        )
        rc = run_health_summary(opts)
        return ok({"exit_code": rc})
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return err([str(exc)])


def run_health_threshold_check_api(config: dict[str, Any]) -> dict[str, Any]:
    """Check thresholds for a health JSON report. Prints status like composed op.

    Config: ``report_file`` (required), optional ``threshold_config_path``, ``strict`` (bool).
    """
    try:
        rf = config.get("report_file")
        if rf is None:
            return err(["report_file is required"])
        tc_path = Path(config["threshold_config_path"]) if config.get("threshold_config_path") else None
        rc = run_health_threshold_check(
            Path(rf),
            tc_path,
            bool(config.get("strict", False)),
        )
        return ok({"exit_code": rc})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


def emit_health_report_view_api(config: dict[str, Any]) -> dict[str, Any]:
    """Load a report and build view lines without running analyzers.

    Config: ``view_kind`` — ``complexity`` | ``srp`` | ``duplicates`` | ``compare``.

    For ``complexity``: ``report_path``, optional ``targets`` (list[str]).

    For ``srp`` | ``duplicates``: ``report_path``.

    For ``compare``: ``pre_path``, ``post_path``.
    """
    try:
        kind = config.get("view_kind")
        if kind == "complexity":
            rp = config.get("report_path")
            if rp is None:
                return err(["report_path is required"])
            path = Path(rp)
            data = load_json_report(path)
            targets = config.get("targets")
            if targets is None:
                targets = list(DEFAULT_COMPLEXITY_TARGET_NAMES)
            lines = list(
                lines_complexity_targets(data, report_path=path, targets=list(targets))
            )
            return ok({"lines": lines})
        if kind == "srp":
            rp = config.get("report_path")
            if rp is None:
                return err(["report_path is required"])
            path = Path(rp)
            data = load_json_report(path)
            top_mod = int(config.get("top_modules", 20))
            lines = list(
                lines_srp_summary(data, report_path=path, top_modules=top_mod)
            )
            return ok({"lines": lines})
        if kind == "duplicates":
            rp = config.get("report_path")
            if rp is None:
                return err(["report_path is required"])
            path = Path(rp)
            data = load_json_report(path)
            top_n = int(config.get("top", 20))
            lines = list(lines_duplication_summary(data, report_path=path, top=top_n))
            return ok({"lines": lines})
        if kind == "compare":
            pre = config.get("pre_path")
            post = config.get("post_path")
            if pre is None or post is None:
                return err(["pre_path and post_path are required"])
            pre_p, post_p = Path(pre), Path(post)
            pre_d = load_json_report(pre_p)
            post_d = load_json_report(post_p)
            if not isinstance(pre_d, dict):
                pre_d = {}
            if not isinstance(post_d, dict):
                post_d = {}
            lines = list(
                lines_health_compare(pre_d, post_d, pre_path=pre_p, post_path=post_p)
            )
            return ok({"lines": lines})
        return err(['view_kind must be "complexity", "srp", "duplicates", or "compare"'])
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


__all__ = [
    "emit_health_report_view_api",
    "run_health_summary_api",
    "run_health_threshold_check_api",
    "run_package_health_cli_api",
]
