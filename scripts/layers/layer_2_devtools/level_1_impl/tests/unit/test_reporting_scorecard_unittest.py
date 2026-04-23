"""Unit tests: consolidated scorecard + numeric score APIs."""

from __future__ import annotations

import json
import sys
import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

_SCRIPTS_ROOT = Path(__file__).resolve().parents[5]

if "layers" not in sys.modules:
    pkg = types.ModuleType("layers")
    pkg.__path__ = [str(_SCRIPTS_ROOT / "layers")]
    sys.modules["layers"] = pkg
if "layers.layer_2_devtools" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools")
    p.__path__ = [str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools")]
    sys.modules["layers.layer_2_devtools"] = p
if "layers.layer_2_devtools.level_0_infra" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra")
    p.__path__ = [str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_0_infra")]
    sys.modules["layers.layer_2_devtools.level_0_infra"] = p
if "layers.layer_2_devtools.level_1_impl" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_1_impl")
    p.__path__ = [str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl")]
    sys.modules["layers.layer_2_devtools.level_1_impl"] = p
if "layers.layer_2_devtools.level_1_impl.level_1" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_1_impl.level_1")
    p.__path__ = [
        str(_SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl" / "level_1")
    ]
    sys.modules["layers.layer_2_devtools.level_1_impl.level_1"] = p


from layers.layer_2_devtools.level_1_impl.level_1.api_health import (
    emit_health_report_view_api,
)
from layers.layer_2_devtools.level_0_infra.level_0.formatting.architecture_score import (
    ScoreConfig,
    compute_architecture_score,
)
from layers.layer_2_devtools.level_0_infra.level_0.formatting.architecture_scorecard_markdown import (
    build_health_markdown_scorecard,
)


class TestReportingScorecard(unittest.TestCase):
    def test_compute_architecture_score_health_only(self) -> None:
        health = {
            "root": ".",
            "dead_code": {"total_unused_imports": 120},
            "file_metrics": {"long_files": [{"module": "a", "lines": 1}]},
            "complexity": {
                "functions": [{"complexity": 20}, {"complexity": 21}],
                "classes": [{"complexity": 50}],
            },
            "duplication": {"total_duplicate_lines": 450},
            "solid": {"srp_violations": [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}]},
        }
        cfg = ScoreConfig(max_score=100)
        res = compute_architecture_score(health=health, manifest=None, config=cfg)
        assert 0 <= res.score <= 100
        assert res.max_score == 100
        assert "health" in res.inputs

    def test_build_health_markdown_scorecard_contains_sections(self) -> None:
        health = {
            "root": ".",
            "complexity": {"classes": [], "functions": []},
            "duplication": {"duplicate_blocks": [], "total_duplicate_lines": 0},
            "solid": {"srp_violations": []},
        }
        md = build_health_markdown_scorecard(health, report_path=Path("health_report.json"))
        assert "# Architecture scorecard (health report)" in md
        assert "## Complexity targets" in md
        assert "## SRP summary" in md
        assert "## Duplication summary" in md

    def test_api_health_scorecard_from_health_report_path(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "health.json"
            p.write_text(
                json.dumps(
                    {
                        "root": ".",
                        "complexity": {"classes": [], "functions": []},
                        "duplication": {"duplicate_blocks": [], "total_duplicate_lines": 0},
                        "solid": {"srp_violations": []},
                    }
                ),
                encoding="utf-8",
            )
            env = emit_health_report_view_api({"view_kind": "scorecard", "report_path": p})
            assert env["status"] == "ok"
            md = env["data"]["markdown"]
            assert "Architecture scorecard" in md

    def test_api_health_score_from_manifest_path(self) -> None:
        with TemporaryDirectory() as td:
            p = Path(td) / "manifest.json"
            p.write_text(
                json.dumps(
                    {
                        "schema_version": "2",
                        "run_id": "unittest",
                        "steps": {"foo": {"status": "ok", "exit_code": 0, "metrics": {}}},
                        "aggregate": {"overall_exit_code": 0, "failed_steps": [], "skipped_steps": []},
                    }
                ),
                encoding="utf-8",
            )
            env = emit_health_report_view_api({"view_kind": "score", "manifest_path": p})
            assert env["status"] == "ok"
            score = env["data"]["score"]
            assert "score" in score
            assert "components" in score

