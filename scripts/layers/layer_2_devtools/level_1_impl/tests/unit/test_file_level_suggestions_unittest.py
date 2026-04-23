"""Unit tests for file level suggestion primitives."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[5]

if "layers" not in sys.modules:
    pkg = types.ModuleType("layers")
    pkg.__path__ = [str(_SCRIPTS / "layers")]
    sys.modules["layers"] = pkg
if "layers.layer_2_devtools" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools")
    p.__path__ = [str(_SCRIPTS / "layers" / "layer_2_devtools")]
    sys.modules["layers.layer_2_devtools"] = p
if "layers.layer_2_devtools.level_0_infra" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra")
    p.__path__ = [str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra")]
    sys.modules["layers.layer_2_devtools.level_0_infra"] = p
if "layers.layer_2_devtools.level_0_infra.level_0" not in sys.modules:
    p = types.ModuleType("layers.layer_2_devtools.level_0_infra.level_0")
    p.__path__ = [
        str(_SCRIPTS / "layers" / "layer_2_devtools" / "level_0_infra" / "level_0")
    ]
    sys.modules["layers.layer_2_devtools.level_0_infra.level_0"] = p


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_PLACEMENT = _load_module_from_path(
    "_file_level_suggestions",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "placement"
    / "file_level_suggestions.py",
)

Evidence = _PLACEMENT.Evidence
LevelPolicy = _PLACEMENT.LevelPolicy
suggest_levels = _PLACEMENT.suggest_levels


class TestFileLevelSuggestions(unittest.TestCase):
    def test_outgoing_lb_suggests_move_up(self) -> None:
        policy = LevelPolicy(min_level_delta_for_outgoing=1, max_level_delta_for_incoming=-1)
        rows = suggest_levels(
            modules=["level_1.a"],
            module_level={"level_1.a": 1},
            outgoing_level_refs={
                "level_1.a": [Evidence(module="level_1.a", referenced="level_3", referenced_level=3)]
            },
            incoming_level_refs={},
            policy=policy,
        )
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r.lb_required, 4)
        self.assertEqual(r.status, "ok")
        self.assertEqual(r.suggested_level, 4)

    def test_incoming_ub_conflict(self) -> None:
        policy = LevelPolicy(min_level_delta_for_outgoing=1, max_level_delta_for_incoming=-1)
        rows = suggest_levels(
            modules=["level_5.x"],
            module_level={"level_5.x": 5},
            outgoing_level_refs={
                "level_5.x": [Evidence(module="level_5.x", referenced="level_8", referenced_level=8)]
            },
            incoming_level_refs={
                "level_5.x": [
                    Evidence(module="level_2.y", referenced="level_5", referenced_level=2)
                ]
            },
            policy=policy,
        )
        r = rows[0]
        # LB = 9; UB = importer_level-1 = 1
        self.assertEqual(r.lb_required, 9)
        self.assertEqual(r.ub_allowed, 1)
        self.assertEqual(r.status, "conflict")
        self.assertIsNone(r.suggested_level)

    def test_no_change(self) -> None:
        policy = LevelPolicy(min_level_delta_for_outgoing=1, max_level_delta_for_incoming=-1)
        rows = suggest_levels(
            modules=["level_4.ok"],
            module_level={"level_4.ok": 4},
            outgoing_level_refs={
                "level_4.ok": [Evidence(module="level_4.ok", referenced="level_2", referenced_level=2)]
            },
            incoming_level_refs={},
            policy=policy,
        )
        r = rows[0]
        self.assertEqual(r.lb_required, 3)
        self.assertEqual(r.suggested_level, 4)
        self.assertEqual(r.status, "no_change")


if __name__ == "__main__":
    unittest.main()

