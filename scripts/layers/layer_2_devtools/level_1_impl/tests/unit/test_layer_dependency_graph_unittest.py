import unittest


class TestLayerDependencyGraphBuckets(unittest.TestCase):
    def _load(self):
        # Import by path to avoid importing the full layers package.
        import importlib.util
        from pathlib import Path

        here = Path(__file__).resolve()
        scripts_root = None
        for parent in (here, *here.parents):
            if parent.is_dir() and parent.name == "scripts":
                scripts_root = parent
                break
        self.assertIsNotNone(scripts_root)
        tool = (
            scripts_root
            / "layers"
            / "layer_2_devtools"
            / "level_1_impl"
            / "level_2"
            / "layer_dependency_graph.py"
        )
        spec = importlib.util.spec_from_file_location("_ldg", str(tool))
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        mod = importlib.util.module_from_spec(spec)
        import sys

        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_bucket_layer0(self):
        mod = self._load()
        self.assertEqual(
            mod._bucket_for_module("layers.layer_0_core.level_2.analysis.cv_analysis"),
            "layer_0_level_2",
        )

    def test_bucket_competition_infra(self):
        mod = self._load()
        self.assertEqual(
            mod._bucket_for_module("layers.layer_1_competition.level_0_infra.level_3.trainer.feature_extraction"),
            "competition_infra_level_3",
        )

    def test_bucket_contest(self):
        mod = self._load()
        self.assertEqual(
            mod._bucket_for_module(
                "layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ranking.reference_ensemble_dispatch"
            ),
            "contest_level_arc_agi_2_level_1",
        )

    def test_violation_layer0_upward(self):
        mod = self._load()
        self.assertEqual(
            mod._violation_reason("layer_0_level_2", "layer_0_level_3"),
            "upward_layer_0_core",
        )
        self.assertIsNone(mod._violation_reason("layer_0_level_3", "layer_0_level_2"))

    def test_violation_contest_upward_same_slug(self):
        mod = self._load()
        self.assertEqual(
            mod._violation_reason("contest_level_arc_agi_2_level_1", "contest_level_arc_agi_2_level_2"),
            "upward_contest_tier",
        )
        self.assertIsNone(
            mod._violation_reason("contest_level_arc_agi_2_level_2", "contest_level_arc_agi_2_level_1")
        )


if __name__ == "__main__":
    unittest.main()

