"""Unit tests for promotion/demotion suggestion primitives."""

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
    "_promotion_demotion_suggestions",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "placement"
    / "promotion_demotion_suggestions.py",
)

UsageEvidence = _PLACEMENT.UsageEvidence
HeavyReusePolicy = _PLACEMENT.HeavyReusePolicy
suggest_promotions = _PLACEMENT.suggest_promotions
suggest_demotions = _PLACEMENT.suggest_demotions


class TestPromotionDemotionSuggestions(unittest.TestCase):
    def test_promotion_heavy_reuse_ok(self) -> None:
        policy = HeavyReusePolicy(
            min_total_inbound=4, min_distinct_importers=4, min_distinct_levels=2
        )
        incoming = {
            "level_2.util": [
                UsageEvidence("level_3.a", 3),
                UsageEvidence("level_3.b", 3),
                UsageEvidence("level_4.c", 4),
                UsageEvidence("level_4.d", 4),
            ]
        }
        rows = suggest_promotions(
            modules=["level_2.util"],
            module_level={"level_2.util": 2},
            incoming=incoming,
            policy=policy,
        )
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertTrue(r.heavy_reuse)
        # Promotion = +1 but bounded by max_importer-1 (4-1=3).
        self.assertEqual(r.suggested_level, 3)
        self.assertEqual(r.status, "ok")

    def test_promotion_not_heavy_reuse_no_change(self) -> None:
        policy = HeavyReusePolicy(
            min_total_inbound=10, min_distinct_importers=5, min_distinct_levels=2
        )
        incoming = {"level_2.util": [UsageEvidence("level_3.a", 3)]}
        rows = suggest_promotions(
            modules=["level_2.util"],
            module_level={"level_2.util": 2},
            incoming=incoming,
            policy=policy,
        )
        r = rows[0]
        self.assertFalse(r.heavy_reuse)
        self.assertEqual(r.status, "no_change")

    def test_demotion_suggests_lower_level(self) -> None:
        incoming = {"level_6.model": [UsageEvidence("level_1.a", 1), UsageEvidence("level_3.b", 3)]}
        rows = suggest_demotions(
            modules=["level_6.model"],
            module_level={"level_6.model": 6},
            incoming=incoming,
        )
        r = rows[0]
        self.assertEqual(r.status, "ok")
        self.assertEqual(r.suggested_level, 4)

    def test_empty_incoming_skipped(self) -> None:
        rows = suggest_demotions(
            modules=["level_2.x"],
            module_level={"level_2.x": 2},
            incoming={},
        )
        self.assertEqual(rows[0].status, "skipped")


if __name__ == "__main__":
    unittest.main()

